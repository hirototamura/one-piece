"""Export tracked history and explicitly selected real-run families, excluding local tests."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

from onepiece.model import canonical_bytes
from onepiece.store import MAX_BUNDLE_BYTES, MAX_BUNDLE_ENTRIES, _bundle_compression, file_sha256

from onepiece import Store


def export(output: Path, run_ids: set[str]) -> dict:
    project = Path(__file__).resolve().parent
    repository = project.parents[1]
    source = project / "store"
    tracked = subprocess.check_output(
        ["git", "ls-files", "--", "projects/balancing-cube/store/commits/*/records.json"],
        cwd=repository, text=True).splitlines()
    commits = {(repository / name).parent.name for name in tracked}
    discovered = set()
    selected_records = 0
    for path in (source / "commits").glob("*/records.json"):
        records = json.loads(path.read_text(encoding="utf-8"))
        families = {record["id"].split(".")[0] for record in records}
        if families & run_ids:
            if not families <= run_ids:
                raise ValueError("A selected commit also contains an unselected run family")
            discovered.update(families)
            selected_records += len(records)
            commits.add(path.parent.name)
    if discovered != run_ids:
        raise ValueError("Missing requested run IDs: " + ", ".join(sorted(run_ids - discovered)))
    with tempfile.TemporaryDirectory(prefix="onepiece-campaign-publication-") as temporary:
        target = Path(temporary)
        for commit in sorted(commits):
            shutil.copytree(source / "commits" / commit, target / "commits" / commit)
        store = Store(target)
        # Object bytes can have been deduplicated into an unselected local
        # commit. Restore only needed hashes, without importing that commit's
        # unrelated acceptance records or changing any canonical JSON.
        source_store = Store(source)
        original_records = store.records("balancing-cube")
        missing = {}
        for record in original_records:
            for artifact in record["artifacts"]:
                try:
                    store.artifact_path(artifact)
                except ValueError:
                    missing[artifact["sha256"]] = source_store.artifact_path(artifact).read_bytes()
        if missing:
            store.import_records(original_records, artifact_objects=missing)
        integrity = store.check("balancing-cube")
        if not integrity["ok"]:
            raise ValueError("Publication store failed integrity checks: " + "; ".join(integrity["errors"]))
        # Each pack is a normal, bounded One-Piece bundle. Its references resolve
        # against the Git metadata checkout; no ZIP guard or reference rule changes.
        batches, batch, objects, size = [], [], set(), 0
        for record in original_records:
            hashes = {a["sha256"] for a in record["artifacts"]}
            added = sum(store.artifact_path({"sha256": sha}).stat().st_size for sha in hashes - objects)
            added += len(canonical_bytes(record)) + 2
            if batch and (size + added > 400 * 1024 * 1024 or len(objects | hashes) > MAX_BUNDLE_ENTRIES - 2):
                batches.append(batch)
                batch, objects, size = [], set(), 0
                added = sum(store.artifact_path({"sha256": sha}).stat().st_size for sha in hashes) + len(canonical_bytes(record)) + 2
            if added > 400 * 1024 * 1024:
                raise ValueError("One record exceeds the publication pack budget")
            batch.append(record)
            objects.update(hashes)
            size += added
        if batch:
            batches.append(batch)
        restored_path = target / "roundtrip"
        # Start from the exact metadata-only checkout that a Git clone provides.
        for commit in sorted(commits):
            for name in ("records.json", "manifest.json"):
                src = source / "commits" / commit / name
                dst = restored_path / "commits" / commit / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        restored = Store(restored_path)
        packs = []
        for index, batch in enumerate(batches, 1):
            path = output.with_name(f"{output.stem}-part{index:02d}.zip")
            path.parent.mkdir(parents=True, exist_ok=True)
            manifest = canonical_bytes({"schema_version": "1.0", "format": "onepiece-evidence-bundle", "records": batch})
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("bundle.json", manifest, compress_type=_bundle_compression([manifest]))
                for sha in sorted({a["sha256"] for r in batch for a in r["artifacts"]}):
                    obj = store.artifact_path({"sha256": sha})
                    with obj.open("rb") as stream:
                        compression = _bundle_compression(iter(lambda: stream.read(1024 * 1024), b""))
                    archive.write(obj, "objects/" + sha, compress_type=compression)
                if len(archive.infolist()) > MAX_BUNDLE_ENTRIES or sum(i.file_size for i in archive.infolist()) > MAX_BUNDLE_BYTES:
                    raise ValueError("Pack exceeds One-Piece ZIP limits")
            sha = file_sha256(path)
            restored.import_bundle(path, expected_sha256=sha)
            packs.append({"filename": path.name, "sha256": sha, "size_bytes": path.stat().st_size, "records": len(batch)})
        if not restored.check("balancing-cube")["ok"] or restored.records("balancing-cube") != original_records:
            raise ValueError("Publication packs failed metadata-clone rehydration")
        for pack in packs:
            duplicate = restored.import_bundle(output.parent / pack["filename"], expected_sha256=pack["sha256"])
            if duplicate["commit_id"] is not None:
                raise ValueError("Duplicate bundle delivery created new records")
    return {"schema_version": "1.0", "format": "onepiece-metadata-clone-evidence-packs",
            "project_id": "balancing-cube", "packs": packs, "run_ids": sorted(run_ids),
            "canonical_records": len(original_records), "selected_records": selected_records,
            "canonical_commits": len(commits), "metadata_checkout_required": True,
            "roundtrip_verified": True, "duplicate_delivery_verified": True}



def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--run-id", action="append", required=True)
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args()
    result = export(args.output.resolve(), set(args.run_id))
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.metadata:
        args.metadata.parent.mkdir(parents=True, exist_ok=True)
        args.metadata.write_text(encoded, encoding="utf-8")
    print(encoded)


if __name__ == "__main__":
    main()
