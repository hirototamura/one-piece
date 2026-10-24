"""Small SysML v2-inspired model vocabulary; not a SysML compiler or certification."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any

EDGE_TYPES = frozenset({"derive", "satisfy", "verify", "allocate", "constrain"})
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,199}$")
REV_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
KIND_RE = re.compile(r"^[a-z][a-z0-9_]{0,79}$")
REQUIRED = {"schema_version", "project_id", "id", "revision", "kind", "product_node", "created_at", "actor", "data", "links", "artifacts"}


class RecordError(ValueError):
    """A record does not satisfy the versioned envelope contract."""


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise RecordError("Records must contain finite JSON values") from exc


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def safe_artifact_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise RecordError("Artifact path must be a nonempty portable relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ("..", ".") for p in value.split("/")) or "" in value.split("/") or ":" in path.parts[0]:
        raise RecordError("Unsafe artifact path: " + value)
    return value


def ref(record_or_id: dict | str, revision: str | int | None = None) -> dict:
    if isinstance(record_or_id, dict):
        return {"id": str(record_or_id["id"]), "revision": str(record_or_id["revision"])}
    if revision is None:
        raise RecordError("An explicit revision is required for every reference")
    return {"id": str(record_or_id), "revision": str(revision)}


def validate_record(record: dict) -> dict:
    if not isinstance(record, dict) or REQUIRED - record.keys():
        raise RecordError("Missing envelope fields: " + ", ".join(sorted(REQUIRED - record.keys() if isinstance(record, dict) else REQUIRED)))
    if record["schema_version"] != "1.0":
        raise RecordError("Unsupported schema_version")
    for field in ("project_id", "id"):
        if not isinstance(record[field], str) or not ID_RE.fullmatch(record[field]):
            raise RecordError("Invalid " + field)
    if not isinstance(record["revision"], str) or not REV_RE.fullmatch(record["revision"]):
        raise RecordError("Revision must be an explicit portable string")
    if not isinstance(record["kind"], str) or not KIND_RE.fullmatch(record["kind"]):
        raise RecordError("Invalid record kind")
    if not isinstance(record["product_node"], str) or not record["product_node"].strip():
        raise RecordError("product_node is required")
    try:
        if not isinstance(record["created_at"], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", record["created_at"]):
            raise ValueError("invalid ISO timestamp")
        timestamp = datetime.fromisoformat(record["created_at"].replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            raise ValueError("missing timezone")
    except (TypeError, AttributeError, ValueError) as exc:
        raise RecordError("created_at must be an ISO-8601 timestamp with timezone") from exc
    if not isinstance(record["actor"], dict) or record["actor"].get("type") not in {"human", "agent", "automation"} or not isinstance(record["actor"].get("id"), str) or not record["actor"]["id"]:
        raise RecordError("actor requires type human/agent/automation and nonempty id")
    if not isinstance(record["data"], dict) or not isinstance(record["links"], list) or not isinstance(record["artifacts"], list):
        raise RecordError("data must be an object; links and artifacts must be arrays")
    for edge in record["links"]:
        if not isinstance(edge, dict) or edge.get("type") not in EDGE_TYPES or not isinstance(edge.get("target"), dict):
            raise RecordError("Unknown or malformed system-model edge")
        target = edge["target"]
        if set(target) != {"id", "revision"} or not isinstance(target["id"], str) or not ID_RE.fullmatch(target["id"]) or not isinstance(target["revision"], str) or not REV_RE.fullmatch(target["revision"]):
            raise RecordError("Link target requires explicit id and revision")
    artifact_paths = set()
    for artifact in record["artifacts"]:
        if not isinstance(artifact, dict):
            raise RecordError("Malformed artifact")
        path = safe_artifact_path(artifact.get("path"))
        if path in artifact_paths:
            raise RecordError("Duplicate artifact path in one record")
        artifact_paths.add(path)
        if not isinstance(artifact.get("sha256"), str) or not SHA_RE.fullmatch(artifact["sha256"]):
            raise RecordError("Every artifact requires a SHA-256 digest")
        if "size_bytes" in artifact and (not isinstance(artifact["size_bytes"], int) or isinstance(artifact["size_bytes"], bool) or artifact["size_bytes"] < 0):
            raise RecordError("Invalid artifact size")
        if "uri" in artifact and not isinstance(artifact["uri"], str):
            raise RecordError("Artifact URI must be a string")
    if record["kind"] == "baseline":
        if record["actor"]["type"] != "human":
            raise RecordError("Only a recorded human action may establish a baseline")
        if not isinstance(record["data"].get("members"), list) or not isinstance(record["data"].get("reason"), str) or not record["data"]["reason"].strip():
            raise RecordError("Baseline requires explicit member revisions and rationale")
        for member in record["data"]["members"]:
            if not isinstance(member, dict) or set(member) != {"id", "revision", "sha256"} or not isinstance(member["id"], str) or not ID_RE.fullmatch(member["id"]) or not isinstance(member["revision"], str) or not REV_RE.fullmatch(member["revision"]) or not isinstance(member["sha256"], str) or not SHA_RE.fullmatch(member["sha256"]):
                raise RecordError("Malformed baseline member")
    data = record["data"]
    physical_claim = any(data.get(field) in (True, "pass", "passed") for field in ("physical_validation", "physical_verified", "physical_pass"))
    if physical_claim and (data.get("evidence_type") not in {"hardware_test", "physical_test", "hardware_measurement", "field_test"} or not record["artifacts"]):
        raise RecordError("Numerical/simulation or missing evidence cannot establish physical validation")
    canonical_bytes(record)
    return record


def make_record(*, project_id: str, id: str, kind: str, product_node: str = "system", revision: str | int = "1", data: dict | None = None, links: list | None = None, artifacts: list | None = None, actor: dict | None = None, created_at: str | None = None) -> dict:
    record = {"schema_version": "1.0", "project_id": project_id, "id": id, "revision": str(revision), "kind": kind, "product_node": product_node, "created_at": created_at or datetime.now(timezone.utc).isoformat(), "actor": actor or {"type": "agent", "id": "onepiece"}, "data": data or {}, "links": links or [], "artifacts": artifacts or []}
    return validate_record(record)


def record_schema() -> dict:
    """Return the packaged public JSON Schema; domain-specific semantics add checks."""
    from importlib.resources import files
    return json.loads(files("onepiece").joinpath("record.schema.json").read_text(encoding="utf-8"))
