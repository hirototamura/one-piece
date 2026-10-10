"""Immutable JSON commits are authoritative. SQLite is a disposable query index."""
from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import shutil
import sqlite3
import stat
import tempfile
import urllib.parse
import urllib.request
import zipfile
import zlib
from pathlib import Path
from typing import Iterable

from .model import RecordError, SHA_RE, canonical_bytes, digest, make_record, ref, safe_artifact_path, validate_record

MAX_BUNDLE_BYTES = 512 * 1024 * 1024
MAX_BUNDLE_ENTRIES = 20000
MAX_RECORD_BYTES = 8 * 1024 * 1024
MAX_ZIP_EXPANSION_RATIO = 300


class ConflictError(RecordError):
    """A previously recorded revision cannot be overwritten."""


class IntegrityError(RecordError):
    """Stored bytes, references, or imported artifacts are inconsistent."""


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _fsync_file(path: Path, value: bytes) -> None:
    with path.open("wb") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())


def _key(record: dict) -> tuple[str, str, str]:
    return record["project_id"], record["id"], record["revision"]


def _bundle_compression(chunks: Iterable[bytes]) -> int:
    """Keep our own bundles within the reader's expansion-ratio limit."""
    compressor = zlib.compressobj(wbits=-15)
    size = compressed = 0
    for chunk in chunks:
        size += len(chunk)
        compressed += len(compressor.compress(chunk))
    compressed += len(compressor.flush())
    return zipfile.ZIP_STORED if size > max(compressed, 1) * MAX_ZIP_EXPANSION_RATIO else zipfile.ZIP_DEFLATED


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser().resolve()
        self.commits = self.path / "commits"
        self.commits.mkdir(parents=True, exist_ok=True)
        self.index_path = self.path / "index.sqlite"
        with self._lock():
            self._ensure_index()

    @contextlib.contextmanager
    def _lock(self):
        with (self.path / ".write.lock").open("a+b") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _commit_dirs(self) -> list[Path]:
        dirs = []
        for path in self.commits.iterdir():
            if path.name.startswith("."):
                continue
            if not SHA_RE.fullmatch(path.name) or path.is_symlink() or not path.is_dir():
                raise IntegrityError("Unexpected object in canonical commit directory: " + path.name)
            dirs.append(path)
        return sorted(dirs)

    def _signature(self) -> str:
        return digest([p.name for p in self._commit_dirs()])

    def _load(self) -> list[tuple[dict, str]]:
        records = {}
        for commit in self._commit_dirs():
            record_path, manifest_path = commit / "records.json", commit / "manifest.json"
            if record_path.is_symlink() or manifest_path.is_symlink():
                raise IntegrityError("Symlink in canonical record storage")
            try:
                data = json.loads(record_path.read_bytes())
                manifest = json.loads(manifest_path.read_bytes())
            except (OSError, ValueError) as exc:
                raise IntegrityError("Unreadable canonical commit: " + commit.name) from exc
            records_hash = digest(data)
            identity = digest({"records_sha256": records_hash, "objects": manifest.get("objects", [])}) if "commit_sha256" in manifest else records_hash
            if not isinstance(data, list) or manifest.get("schema_version") != "1.0" or manifest.get("record_count") != len(data) or records_hash != manifest.get("records_sha256") or identity != commit.name or ("commit_sha256" in manifest and manifest["commit_sha256"] != commit.name):
                raise IntegrityError("Canonical commit digest mismatch: " + commit.name)
            for record in data:
                validate_record(record)
                k = _key(record)
                if k in records and canonical_bytes(records[k][0]) != canonical_bytes(record):
                    raise ConflictError("Conflicting stored revision: " + "/".join(k))
                records[k] = record, commit.name
        return [records[k] for k in sorted(records)]

    @staticmethod
    def _check_references(records: Iterable[dict]) -> None:
        records = list(records)
        by_key = {_key(r): r for r in records}
        ancestry = {}
        for record in records:
            for edge in record["links"]:
                target = edge["target"]
                target_key = (record["project_id"], target["id"], target["revision"])
                if target_key not in by_key:
                    raise IntegrityError(f"Dangling {edge['type']} link from {record['id']}@{record['revision']} to {target['id']}@{target['revision']}")
                sk, tk, relation = record["kind"], by_key[target_key]["kind"], edge["type"]
                valid = relation == "derive" and sk == tk
                valid |= relation == "satisfy" and sk in {"design", "product", "design_candidate", "candidate"} and tk == "requirement"
                valid |= relation == "verify" and sk in {"evidence", "verification", "evaluation", "simulation_run", "analysis_result", "verification_coverage"} and tk in {"requirement", "test_case", "verification_case"}
                valid |= relation == "allocate" and sk in {"requirement", "function", "kdp", "parameter", "model_parameter", "design_parameter"} and tk == "product"
                valid |= relation == "constrain" and sk in {"constraint", "requirement", "specification"} and tk in {"parameter", "model_parameter", "kdp", "design_parameter", "design", "product", "model", "simulation_snapshot"}
                if not valid:
                    raise IntegrityError(f"Invalid {relation} direction: {sk} → {tk}")
                if relation == "derive":
                    ancestry.setdefault(_key(record), []).append(target_key)
        visiting, visited = set(), set()
        def visit(node):
            if node in visiting:
                raise IntegrityError("Cycle in derive ancestry")
            if node in visited:
                return
            visiting.add(node)
            for parent in ancestry.get(node, []):
                visit(parent)
            visiting.remove(node)
            visited.add(node)
        for node in ancestry:
            visit(node)
        for record in records:
            if record["kind"] == "baseline":
                members = record["data"]["members"]
                seen_members = set()
                for member in members:
                    member_key = (record["project_id"], member["id"], member["revision"])
                    if member_key not in by_key:
                        raise IntegrityError("Dangling baseline member: " + member["id"])
                    if member_key in seen_members or member_key == _key(record):
                        raise IntegrityError("Duplicate or self-referencing baseline member")
                    seen_members.add(member_key)
                    if digest(by_key[member_key]) != member["sha256"]:
                        raise IntegrityError("Baseline member digest mismatch: " + member["id"])
        Store._check_model_bindings(records, by_key)

    @staticmethod
    def _check_model_bindings(records: list[dict], by_key: dict) -> None:
        """Keep resolved model leaves and preserved KDP registry values distinct."""
        def referenced(record, reference, expected_kind):
            if not isinstance(reference, dict) or set(reference) != {"id", "revision"}:
                raise IntegrityError("Model binding requires an exact revision reference")
            try:
                target = by_key[(record["project_id"], reference["id"], reference["revision"])]
            except (KeyError, TypeError) as exc:
                raise IntegrityError("Dangling model binding reference") from exc
            if target["kind"] != expected_kind:
                raise IntegrityError("Model binding reference kind mismatch")
            return target

        def model_value(snapshot, path):
            if not isinstance(path, str) or not path or any(not part for part in path.split(".")):
                raise IntegrityError("Invalid model binding path")
            try:
                value = snapshot["data"]["model"]
                for part in path.split("."):
                    if isinstance(value, list):
                        if not part.isdigit():
                            raise ValueError("Invalid list index")
                        value = value[int(part)]
                    else:
                        value = value[part]
                return value
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                raise IntegrityError("Model binding path is absent from authoritative snapshot") from exc

        def binding_valid(record, snapshot, binding):
            if not isinstance(binding, dict):
                raise IntegrityError("Malformed model parameter registry binding")
            path = binding.get("model_path")
            actual = model_value(snapshot, path)
            parameter = referenced(record, binding.get("parameter_ref"), "parameter")
            registry = parameter["data"]
            if (binding.get("value_source") != "model" or registry.get("model_path") != path
                    or "value" not in registry or "registered_value" not in binding
                    or binding["registered_value"] != registry["value"]
                    or "resolved_value" not in binding or binding["resolved_value"] != actual
                    or not isinstance(binding.get("values_match"), bool)
                    or binding["values_match"] != (registry["value"] == actual)):
                raise IntegrityError("Model parameter registry binding disagrees with frozen records")
            return parameter

        for record in records:
            if record["kind"] == "simulation_snapshot":
                seen = set()
                for binding in record["data"].get("parameter_bindings", []):
                    binding_valid(record, record, binding)
                    if binding["model_path"] in seen:
                        raise IntegrityError("Duplicate model parameter binding path")
                    seen.add(binding["model_path"])
            elif record["kind"] == "model_parameter":
                data = record["data"]
                snapshot = referenced(record, data.get("value_source"), "simulation_snapshot")
                path = data.get("model_path")
                actual = model_value(snapshot, path)
                if ("value" not in data or data["value"] != actual
                        or data.get("authoritative_field") != "data.model." + path
                        or not isinstance(data.get("unit"), str) or not data["unit"].strip()):
                    raise IntegrityError("Model parameter leaf disagrees with authoritative snapshot")
                bindings = [b for b in snapshot["data"].get("parameter_bindings", []) if b.get("model_path") == path]
                binding = data.get("registry_binding")
                if bindings:
                    if len(bindings) != 1 or binding != bindings[0]:
                        raise IntegrityError("Model parameter binding differs from snapshot binding")
                    parameter = binding_valid(record, snapshot, binding)
                    if data["unit"] != parameter["data"].get("unit"):
                        raise IntegrityError("Model parameter unit differs from registry binding")
                elif binding is not None:
                    raise IntegrityError("Model parameter binding is absent from snapshot")

    def _ensure_index(self) -> None:
        signature = self._signature()
        canonical = {_key(r): r for r, _ in self._load()}
        try:
            with sqlite3.connect(self.index_path) as db:
                current = db.execute("SELECT value FROM meta WHERE key='commit_signature'").fetchone()
                indexed = db.execute("SELECT project_id,id,revision,digest,body,kind,product_node,created_at FROM records").fetchall()
            if current and current[0] == signature and len(indexed) == len(canonical) and all(tuple(row[:3]) in canonical and digest(canonical[tuple(row[:3])]) == row[3] == digest(json.loads(row[4])) and tuple(row[5:]) == tuple(canonical[tuple(row[:3])][field] for field in ("kind", "product_node", "created_at")) for row in indexed):
                return
        except (sqlite3.Error, ValueError):
            pass
        self._rebuild_index()

    def rebuild_index(self) -> dict:
        with self._lock():
            return self._rebuild_index()

    def _rebuild_index(self) -> dict:
        entries = self._load()
        self._check_references(r for r, _ in entries)
        fd, temporary = tempfile.mkstemp(prefix=".index-", suffix=".sqlite", dir=self.path)
        os.close(fd)
        temporary = Path(temporary)
        try:
            with sqlite3.connect(temporary) as db:
                db.executescript("""
                    CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                    CREATE TABLE records(project_id TEXT NOT NULL,id TEXT NOT NULL,revision TEXT NOT NULL,kind TEXT NOT NULL,product_node TEXT NOT NULL,created_at TEXT NOT NULL,digest TEXT NOT NULL,body TEXT NOT NULL,commit_id TEXT NOT NULL,PRIMARY KEY(project_id,id,revision));
                    CREATE TABLE edges(project_id TEXT NOT NULL,source_id TEXT NOT NULL,source_revision TEXT NOT NULL,type TEXT NOT NULL,target_id TEXT NOT NULL,target_revision TEXT NOT NULL);
                    CREATE INDEX records_kind ON records(project_id,kind,product_node);
                    CREATE INDEX edges_target ON edges(project_id,target_id,target_revision);
                """)
                for record, commit in entries:
                    db.execute("INSERT INTO records VALUES(?,?,?,?,?,?,?,?,?)", (*_key(record), record["kind"], record["product_node"], record["created_at"], digest(record), canonical_bytes(record).decode(), commit))
                    for edge in record["links"]:
                        db.execute("INSERT INTO edges VALUES(?,?,?,?,?,?)", (*_key(record), edge["type"], edge["target"]["id"], edge["target"]["revision"]))
                db.execute("INSERT INTO meta VALUES('commit_signature',?)", (self._signature(),))
                db.commit()
            os.replace(temporary, self.index_path)
        finally:
            temporary.unlink(missing_ok=True)
        return {"records": len(entries), "index": str(self.index_path)}

    def records(self, project_id: str | None = None, kinds: list[str] | None = None) -> list[dict]:
        with self._lock():
            self._ensure_index()
            clauses, args = [], []
            if project_id:
                clauses.append("project_id=?")
                args.append(project_id)
            if kinds:
                clauses.append("kind IN (" + ",".join("?" for _ in kinds) + ")")
                args.extend(kinds)
            query = "SELECT body FROM records" + (" WHERE " + " AND ".join(clauses) if clauses else "") + " ORDER BY created_at,id,revision"
            with sqlite3.connect(self.index_path) as db:
                return [json.loads(row[0]) for row in db.execute(query, args)]

    def import_records(self, records: Iterable[dict], artifacts_root: str | Path | None = None, *, artifact_objects: dict[str, bytes] | None = None) -> dict:
        # Copy callers' objects so concurrent mutation cannot alter validated bytes.
        incoming = json.loads(canonical_bytes(list(records)))
        for record in incoming:
            validate_record(record)
            if len(canonical_bytes(record)) > MAX_RECORD_BYTES:
                raise RecordError("Record exceeds the 8 MiB envelope limit")
        root = Path(artifacts_root).expanduser().resolve() if artifacts_root is not None else None
        with self._lock():
            previous = self._load()
            known = {_key(record): record for record, _ in previous}
            new, unchanged, seen = [], 0, set()
            for record in incoming:
                k = _key(record)
                if k in seen:
                    if canonical_bytes(known[k]) != canonical_bytes(record):
                        raise ConflictError("Conflicting revisions inside import: " + "/".join(k))
                    unchanged += 1
                    continue
                seen.add(k)
                if k in known:
                    if canonical_bytes(known[k]) != canonical_bytes(record):
                        raise ConflictError("Revision is immutable: " + "/".join(k))
                    unchanged += 1
                else:
                    known[k] = record
                    new.append(record)
            self._check_references(known.values())
            existing_objects, missing_objects = {}, set()
            for record in incoming:
                for artifact in record["artifacts"]:
                    sha = artifact["sha256"]
                    if sha not in existing_objects:
                        existing_objects[sha] = self._find_object(sha)
                    existing = existing_objects[sha]
                    if existing is None:
                        missing_objects.add(sha)
                    elif "size_bytes" in artifact and existing.stat().st_size != artifact["size_bytes"]:
                        raise IntegrityError("Artifact size mismatch: " + artifact["path"])
            if not new and not missing_objects:
                return {"imported": 0, "unchanged": unchanged, "commit_id": None, "restored_artifacts": 0}
            new.sort(key=_key)
            stage = Path(tempfile.mkdtemp(prefix=".import-", dir=self.commits))
            try:
                objects = stage / "objects"
                objects.mkdir()
                for record in incoming:
                    for artifact in record["artifacts"]:
                        sha = artifact["sha256"]
                        if sha not in missing_objects:
                            continue
                        target = objects / sha
                        if target.exists():
                            if "size_bytes" in artifact and target.stat().st_size != artifact["size_bytes"]:
                                raise IntegrityError("Artifact size mismatch: " + artifact["path"])
                            continue
                        if artifact_objects is not None and sha in artifact_objects:
                            content = artifact_objects[sha]
                            if not isinstance(content, bytes) or hashlib.sha256(content).hexdigest() != sha:
                                raise IntegrityError("Artifact digest mismatch: " + artifact["path"])
                            _fsync_file(target, content)
                        elif root is not None:
                            source = root / safe_artifact_path(artifact["path"])
                            resolved = source.resolve()
                            try:
                                resolved.relative_to(root)
                            except ValueError as exc:
                                raise IntegrityError("Artifact escapes source root") from exc
                            if not resolved.is_file() or source.is_symlink():
                                raise IntegrityError("Artifact must be a regular source file")
                            with resolved.open("rb") as source_file, target.open("wb") as dest:
                                shutil.copyfileobj(source_file, dest)
                                dest.flush()
                                os.fsync(dest.fileno())
                            if file_sha256(target) != sha:
                                raise IntegrityError("Artifact digest mismatch: " + artifact["path"])
                        else:
                            existing = self._find_object(sha)
                            if existing is None:
                                raise IntegrityError("Artifact bytes are required: " + artifact["path"])
                            shutil.copyfile(existing, target)
                        if "size_bytes" in artifact and target.stat().st_size != artifact["size_bytes"]:
                            raise IntegrityError("Artifact size mismatch: " + artifact["path"])
                records_hash = digest(new)
                object_hashes = sorted(p.name for p in objects.iterdir())
                commit_id = digest({"records_sha256": records_hash, "objects": object_hashes})
                _fsync_file(stage / "records.json", canonical_bytes(new))
                _fsync_file(stage / "manifest.json", canonical_bytes({"schema_version": "1.0", "records_sha256": records_hash, "record_count": len(new), "objects": object_hashes, "commit_sha256": commit_id}))
                destination = self.commits / commit_id
                if destination.exists():
                    # A metadata-only re-clone can retain an objects-only restore
                    # commit with this same identity. Restore its missing object
                    # directory atomically without rewriting canonical JSON.
                    if any((destination / name).read_bytes() != (stage / name).read_bytes()
                           for name in ("records.json", "manifest.json")):
                        raise ConflictError("Canonical commit identity collision")
                    object_target = destination / "objects"
                    if object_target.is_symlink() or (object_target.exists() and any(object_target.iterdir())):
                        raise IntegrityError("Unexpected existing objects in restore commit")
                    os.replace(objects, object_target)
                    directory_to_sync = destination
                else:
                    # No partial record batch becomes visible before this rename.
                    os.replace(stage, destination)
                    directory_to_sync = self.commits
                directory_fd = os.open(directory_to_sync, os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
                self._rebuild_index()
            finally:
                if stage.exists():
                    shutil.rmtree(stage)
            return {"imported": len(new), "unchanged": unchanged, "commit_id": commit_id, "restored_artifacts": len(missing_objects)}

    def _find_object(self, sha: str) -> Path | None:
        for commit in self._commit_dirs():
            obj = commit / "objects" / sha
            if obj.exists():
                if obj.is_symlink() or not obj.is_file() or file_sha256(obj) != sha:
                    raise IntegrityError("Corrupt artifact object: " + sha)
                return obj
        return None

    def artifact_path(self, artifact: dict) -> Path:
        if not SHA_RE.fullmatch(artifact.get("sha256", "")):
            raise IntegrityError("Invalid artifact digest")
        path = self._find_object(artifact["sha256"])
        if path is None:
            raise IntegrityError("Missing artifact object")
        return path

    def context(self, project_id: str, *, product_node: str | None = None, kinds: list[str] | None = None, max_designs: int = 20, max_evidence: int = 50, snapshot_ref: dict | None = None) -> dict:
        if max_designs < 0 or max_evidence < 0:
            raise RecordError("Context limits must be nonnegative")
        records = self.records(project_id)
        # Requirements, KDPs, and assumptions retain their exact units/uncertainty even when evidence is bounded.
        always = {"requirement", "kdp", "parameter", "model_parameter", "simulation_snapshot", "campaign_summary", "verification_coverage", "design_parameter", "assumption", "risk", "interface", "product", "system_model", "baseline"}
        snapshot = None
        if snapshot_ref is not None:
            snapshot = next((r for r in records if r["kind"] == "simulation_snapshot" and ref(r) == snapshot_ref), None)
            if snapshot is None:
                raise RecordError("Context snapshot requires an existing exact revision")
            # Keep every requirement/parameter with its units and uncertainty.
            # Historical snapshots/aggregates stay queryable in the Store; a
            # scoped agent view avoids repeating their embedded registries.
            always -= {"simulation_snapshot", "campaign_summary", "verification_coverage"}
        design_kinds = {"design", "design_candidate", "candidate"}
        evidence_kinds = {"evidence", "evaluation", "artifact", "simulation_run", "trial", "verification", "analysis_result"}
        selected, design_count, evidence_count = [], 0, 0
        eligible = [r for r in records if (product_node is None or r["product_node"] == product_node or r["product_node"].startswith(product_node + "/")) and (not kinds or r["kind"] in kinds)]
        # Keep requirements/KDP from the whole project, not only the selected subsystem, to preserve system context.
        eligible_keys = {_key(r) for r in eligible} | {_key(r) for r in records if r["kind"] in always}
        if snapshot is not None:
            eligible_keys -= {_key(r) for r in records if r["kind"] in {"simulation_snapshot", "campaign_summary", "verification_coverage"}}
            eligible_keys.add(_key(snapshot))
        for record in reversed(records):
            if _key(record) not in eligible_keys:
                continue
            kind = record["kind"]
            if kind in design_kinds:
                if design_count >= max_designs:
                    continue
                design_count += 1
            if kind in evidence_kinds:
                if evidence_count >= max_evidence:
                    continue
                evidence_count += 1
            selected.append(record)
        selected.reverse()
        keys = {_key(r) for r in selected}
        omitted_refs = []
        for record in selected:
            for edge in record["links"]:
                target = edge["target"]
                if (project_id, target["id"], target["revision"]) not in keys:
                    omitted_refs.append({"source": ref(record), "type": edge["type"], "target": target, "reason": "context_filter_or_limit"})
        return {"schema_version": "1.0", "project_id": project_id, "records": selected, "counts": {"project_records": len(records), "returned": len(selected), "designs": design_count, "evidence": evidence_count}, "limits": {"max_designs": max_designs, "max_evidence": max_evidence}, "snapshot_ref": snapshot_ref, "omitted_record_count": len(records) - len(selected), "omitted_references": omitted_refs, "semantics": "All project requirements, KDPs, assumptions and risks retained verbatim; returned evidence/designs are bounded. A snapshot_ref scopes embedded model history to that exact snapshot. Omitted references remain in canonical storage. Simulation/numerical agreement is not physical validation."}

    def check(self, project_id: str | None = None) -> dict:
        errors, warnings, records = [], [], []
        try:
            records = [r for r, _ in self._load() if project_id is None or r["project_id"] == project_id]
            self._check_references(records)
            for record in records:
                for artifact in record["artifacts"]:
                    obj = self.artifact_path(artifact)
                    if "size_bytes" in artifact and obj.stat().st_size != artifact["size_bytes"]:
                        raise IntegrityError("Stored artifact size mismatch")
        except (OSError, ValueError, sqlite3.Error) as exc:
            errors.append(str(exc))
        for record in records:
            data = record["data"]
            if record["kind"] in {"kdp", "parameter", "design_parameter", "model_parameter"} and not isinstance(data.get("unit", data.get("units")), str):
                warnings.append(f"{record['id']}@{record['revision']}: parameter unit is unspecified")
            if record["kind"] == "requirement" and not data.get("success_criteria") and not data.get("acceptance_criteria"):
                warnings.append(f"{record['id']}@{record['revision']}: requirement success criteria not structured")
            if any(data.get(field) in (True, "pass", "passed") for field in ("physical_validation", "physical_verified", "physical_pass")) and (data.get("evidence_type") not in {"hardware_test", "physical_test", "hardware_measurement", "field_test"} or not record["artifacts"]):
                errors.append(f"{record['id']}: numerical/simulation evidence cannot establish physical validation")
        return {"ok": not errors, "errors": errors, "warnings": warnings, "records": len(records), "edges": sum(len(r["links"]) for r in records)}

    def baseline(self, project_id: str, *, id: str, actor: dict, reason: str, revision: str = "1") -> dict:
        if actor.get("type") != "human" or not reason.strip():
            raise RecordError("Baseline requires an explicit human actor and rationale")
        records = self.records(project_id)
        record = make_record(project_id=project_id, id=id, kind="baseline", revision=revision, actor=actor, data={"reason": reason, "scope": "configuration_identity_only_not_physical_acceptance", "members": [{**ref(r), "sha256": digest(r)} for r in records]})
        return self.import_records([record])

    def bundle(self, output: str | Path, project_id: str | None = None) -> dict:
        check = self.check(project_id)
        if not check["ok"]:
            raise IntegrityError("Cannot bundle an invalid store: " + "; ".join(check["errors"]))
        records = self.records(project_id)
        output = Path(output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".bundle-", suffix=".zip", dir=output.parent)
        os.close(fd)
        try:
            with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                manifest = canonical_bytes({"schema_version": "1.0", "format": "onepiece-evidence-bundle", "records": records})
                archive.writestr("bundle.json", manifest, compress_type=_bundle_compression([manifest]))
                objects = {a["sha256"] for r in records for a in r["artifacts"]}
                for sha in sorted(objects):
                    path = self.artifact_path({"sha256": sha})
                    with path.open("rb") as stream:
                        compression = _bundle_compression(iter(lambda: stream.read(1024 * 1024), b""))
                    archive.write(path, "objects/" + sha, compress_type=compression)
                if len(archive.infolist()) > MAX_BUNDLE_ENTRIES or sum(i.file_size for i in archive.infolist()) > MAX_BUNDLE_BYTES:
                    raise IntegrityError("Bundle exceeds entry or uncompressed size limit")
            if Path(temporary).stat().st_size > MAX_BUNDLE_BYTES:
                raise IntegrityError("Bundle exceeds download size limit")
            os.replace(temporary, output)
        finally:
            Path(temporary).unlink(missing_ok=True)
        return {"path": str(output), "sha256": file_sha256(output), "size_bytes": output.stat().st_size, "records": len(records)}

    def import_bundle(self, path: str | Path, *, expected_sha256: str) -> dict:
        path = Path(path).expanduser().resolve()
        if not SHA_RE.fullmatch(expected_sha256) or file_sha256(path) != expected_sha256:
            raise IntegrityError("Bundle SHA-256 mismatch")
        if path.stat().st_size > MAX_BUNDLE_BYTES:
            raise IntegrityError("Bundle exceeds download size limit")
        try:
            with zipfile.ZipFile(path) as archive:
                infos = archive.infolist()
                names = [i.filename for i in infos]
                if len(infos) > MAX_BUNDLE_ENTRIES or len(set(names)) != len(names) or sum(i.file_size for i in infos) > MAX_BUNDLE_BYTES:
                    raise IntegrityError("Bundle has duplicate/excessive entries or excessive uncompressed size")
                for info in infos:
                    name = safe_artifact_path(info.filename)
                    mode = info.external_attr >> 16
                    if stat.S_ISLNK(mode) or info.is_dir() or info.flag_bits & 1 or info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
                        raise IntegrityError("Unsafe ZIP entry")
                    if name != "bundle.json" and not (name.startswith("objects/") and SHA_RE.fullmatch(name.removeprefix("objects/"))):
                        raise IntegrityError("Unexpected bundle entry: " + name)
                    if info.file_size > max(info.compress_size, 1) * MAX_ZIP_EXPANSION_RATIO:
                        raise IntegrityError("Suspicious ZIP expansion ratio")
                manifest = json.loads(archive.read("bundle.json"))
                if manifest.get("schema_version") != "1.0" or manifest.get("format") != "onepiece-evidence-bundle" or not isinstance(manifest.get("records"), list):
                    raise IntegrityError("Unsupported evidence bundle")
                for record in manifest["records"]:
                    validate_record(record)
                objects = {name.removeprefix("objects/"): archive.read(name) for name in names if name.startswith("objects/")}
                required = {a["sha256"] for r in manifest["records"] for a in r.get("artifacts", [])}
                if set(objects) != required:
                    raise IntegrityError("Bundle artifact set is incomplete or contains unreferenced objects")
                return self.import_records(manifest["records"], artifact_objects=objects)
        except (zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
            raise IntegrityError("Malformed evidence bundle") from exc

    def fetch(self, url: str, *, expected_sha256: str) -> dict:
        if not SHA_RE.fullmatch(expected_sha256):
            raise IntegrityError("An explicit bundle SHA-256 is required")
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"https", "file"} or parsed.username or parsed.password or (parsed.scheme == "file" and parsed.netloc not in {"", "localhost"}):
            raise IntegrityError("Fetch accepts HTTPS or local file URLs without embedded credentials")
        fd, filename = tempfile.mkstemp(prefix=".fetch-", suffix=".zip", dir=self.path)
        os.close(fd)
        path = Path(filename)
        try:
            with urllib.request.urlopen(url, timeout=30) as response, path.open("wb") as out:
                final = urllib.parse.urlparse(response.geturl())
                if final.scheme not in {"https", "file"} or final.username or final.password:
                    raise IntegrityError("Unsafe fetch redirect")
                count = 0
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    count += len(chunk)
                    if count > MAX_BUNDLE_BYTES:
                        raise IntegrityError("Download exceeds size limit")
                    out.write(chunk)
            return self.import_bundle(path, expected_sha256=expected_sha256)
        finally:
            path.unlink(missing_ok=True)
