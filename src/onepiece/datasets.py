"""Immutable dataset catalogs and selective, hash-checked private Release retrieval.

These archives preserve research evidence outside Git. Retrieval never imports
records, approves requirements, or changes an engineering baseline.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile

from .model import RecordError, canonical_bytes

SHA = re.compile(r"[0-9a-f]{64}\Z")
SLUG = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
EXCLUDED = {".git", ".DS_Store", "__pycache__", ".pytest_cache", "node_modules", "build", "dist"}
BLOCK = 1024 * 1024
MAX_ARCHIVE_BYTES = 1024 ** 3
MAX_DATASET_BYTES = 8 * 1024 ** 3


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_relative(value: str) -> PurePosixPath:
    if not isinstance(value, str):
        raise RecordError("A dataset path must be a string")
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or "\\" in value or ":" in value
            or any(p in {"", ".", ".."} for p in value.split("/"))):
        raise RecordError(f"Unsafe dataset path: {value}")
    return path


def safe_target(root: Path, relative: str) -> Path:
    target = root.joinpath(*safe_relative(relative).parts)
    if any(p.is_symlink() for p in (target, *target.parents)) or not target.resolve().is_relative_to(root.resolve()):
        raise RecordError(f"Dataset path traverses a symlink or escapes destination: {relative}")
    if any(p.exists() and not p.is_dir() for p in target.parents):
        raise FileExistsError(f"Preserve existing non-directory parent of dataset path: {relative}")
    return target


def _included(path: Path) -> bool:
    return not (any(p in EXCLUDED or p.startswith((".venv", ".env")) for p in path.parts)
                or re.fullmatch(r"index(?: \d+)?\.sqlite(?:-.*)?", path.name)
                or path.name.startswith((".write.lock", ".index-", ".fetch-")))


def _slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]", "-", value)
    return value if value and value[0].isalnum() else "dataset-" + value


def pack_datasets(source: Path, output: Path, *, repository: str, release: str,
                  catalog_id: str) -> dict:
    """Inventory one local archive; retain all originals, excluding disposable caches.

    Existing ZIP/tar files remain raw assets. Directories become independent ZIPs.
    Stable archive names contain their hash; source changes during packing fail.
    """
    source, output = source.resolve(), output.resolve()
    if not source.is_dir() or output == source or output.is_relative_to(source):
        raise RecordError("Select a source directory and an output directory outside it")
    if not SLUG.fullmatch(catalog_id) or not SLUG.fullmatch(release) or not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
        raise RecordError("Invalid catalog ID or GitHub Release location")
    output.mkdir(parents=True, exist_ok=True)
    groups = {}
    skipped = 0
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        if path.is_symlink() or not _included(rel):
            if path.is_file() or path.is_symlink():
                skipped += 1
            continue
        if not path.is_file():
            continue
        if len(rel.parts) > 1:
            group = rel.parts[0]
        elif path.name.endswith((".zip", ".tar.gz", ".tgz")):
            group = "archive-" + path.name
        elif path.suffix in {".py", ".cjs", ".mjs", ".sh"}:
            group = "validation-tools"
        elif path.suffix in {".png", ".jpg", ".webp"}:
            group = "browser-qa-images"
        else:
            group = "acceptance-receipts"
        groups.setdefault(group, []).append(path)
    if not groups:
        raise RecordError("Dataset source contains no eligible files")
    datasets = []
    for group, paths in sorted(groups.items()):
        dataset_id = _slug(group)
        raw = len(paths) == 1 and group.startswith("archive-")
        entries = []
        with tempfile.TemporaryDirectory(prefix=".dataset-", dir=output) as temporary:
            packed = Path(temporary) / "payload"
            archive = None if raw else zipfile.ZipFile(packed, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=3)
            try:
                for path in paths:
                    before = path.stat()
                    logical = (Path(source.name) / path.relative_to(source)).as_posix()
                    safe_relative(logical)
                    hasher = hashlib.sha256()
                    info = zipfile.ZipInfo(logical, date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = (stat.S_IFREG | 0o644) << 16
                    with path.open("rb") as src, (packed.open("wb") if raw else archive.open(info, "w", force_zip64=True)) as dst:
                        while chunk := src.read(BLOCK):
                            hasher.update(chunk)
                            dst.write(chunk)
                    after = path.stat()
                    if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                        raise RecordError(f"Dataset source changed during packing: {logical}")
                    entries.append({"path": logical, "sha256": hasher.hexdigest(), "size_bytes": after.st_size})
            finally:
                if archive:
                    archive.close()
            checksum = file_hash(packed)
            if packed.stat().st_size > MAX_ARCHIVE_BYTES or sum(f["size_bytes"] for f in entries) > MAX_DATASET_BYTES:
                raise RecordError("Dataset is too large; split it into smaller run or acceptance packages")
            extension = "." + paths[0].name.split(".", 1)[-1] if raw else ".zip"
            name = f"{catalog_id}-{dataset_id}-{checksum[:16]}{extension}"
            destination = output / name
            if destination.exists():
                if file_hash(destination) != checksum:
                    raise RecordError("Existing immutable archive name has different bytes")
            else:
                shutil.move(packed, destination)
            datasets.append({
                "id": dataset_id, "title": group, "format": "file" if raw else "zip",
                "tags": ["eclss" if group.startswith("eclss") else "balancing-cube", "historical-validation"],
                "location": {"repository": repository, "release": release, "asset": name},
                "sha256": checksum, "size_bytes": destination.stat().st_size,
                "files": entries,
            })
    catalog = {"schema_version": 1, "format": "onepiece-dataset-catalog", "id": catalog_id,
               "created_at": datetime.now(timezone.utc).isoformat(), "visibility": "private",
               "scope": "Historical run evidence and acceptance records; archive storage does not establish engineering verification.",
               "excluded": {"policy": "Git metadata, symlinks, caches, environments, builds and disposable SQLite indexes", "file_count": skipped},
               "datasets": datasets}
    path = output / "catalog.json"
    path.write_bytes(canonical_bytes(catalog) + b"\n")
    load_catalog(path)  # Validate the published contract before returning it.
    return {"catalog": str(path), "sha256": file_hash(path), "datasets": len(datasets),
            "files": sum(len(d["files"]) for d in datasets), "archive_bytes": sum(d["size_bytes"] for d in datasets)}


def load_catalog(path: Path) -> dict:
    catalog = json.loads(Path(path).read_bytes())
    if not isinstance(catalog, dict) or catalog.get("schema_version") != 1 or catalog.get("format") != "onepiece-dataset-catalog":
        raise RecordError("Unsupported dataset catalog")
    if not isinstance(catalog.get("id"), str) or not SLUG.fullmatch(catalog["id"]):
        raise RecordError("Invalid catalog ID")
    datasets = catalog.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        raise RecordError("Dataset catalog is empty")
    ids, all_paths = set(), set()
    for dataset in datasets:
        if not isinstance(dataset, dict):
            raise RecordError("A dataset entry must be an object")
        id = dataset.get("id", "")
        if not isinstance(id, str) or not SLUG.fullmatch(id) or id in ids:
            raise RecordError("Invalid or duplicate dataset ID")
        ids.add(id)
        if dataset.get("format") not in {"file", "zip"} or not isinstance(dataset.get("sha256"), str) or not SHA.fullmatch(dataset["sha256"]):
            raise RecordError("Invalid dataset archive format or digest")
        if not isinstance(dataset.get("size_bytes"), int) or not 0 <= dataset["size_bytes"] <= MAX_ARCHIVE_BYTES:
            raise RecordError("Invalid dataset archive size")
        location = dataset.get("location", {})
        if not isinstance(location, dict) or not isinstance(dataset.get("tags", []), list) or any(not isinstance(t, str) for t in dataset.get("tags", [])):
            raise RecordError("Invalid dataset location or tags")
        for field in ("release", "asset"):
            if not isinstance(location.get(field), str) or not SLUG.fullmatch(location[field]):
                raise RecordError("Invalid GitHub Release asset location")
        if not isinstance(location.get("repository"), str) or not re.fullmatch(r"[\w.-]+/[\w.-]+", location["repository"]):
            raise RecordError("Invalid GitHub repository")
        entries = dataset.get("files")
        if not isinstance(entries, list) or not entries or (dataset["format"] == "file" and len(entries) != 1):
            raise RecordError("Invalid dataset file manifest")
        for item in entries:
            if not isinstance(item, dict):
                raise RecordError("Invalid file manifest entry")
            safe_relative(item.get("path"))
            if item["path"] in all_paths or not isinstance(item.get("sha256"), str) or not SHA.fullmatch(item["sha256"]):
                raise RecordError("Duplicate dataset path or invalid file hash")
            all_paths.add(item["path"])
            if not isinstance(item.get("size_bytes"), int) or not 0 <= item["size_bytes"] <= MAX_DATASET_BYTES:
                raise RecordError("Invalid dataset file size")
        if sum(item["size_bytes"] for item in entries) > MAX_DATASET_BYTES:
            raise RecordError("Dataset expansion exceeds the catalog limit")
        if dataset["format"] == "file" and (entries[0]["sha256"], entries[0]["size_bytes"]) != (dataset["sha256"], dataset["size_bytes"]):
            raise RecordError("Raw asset does not match its file manifest")
    return catalog


def select_datasets(catalog: dict, ids: list[str] | None = None, query: str = "") -> list[dict]:
    known = {d["id"] for d in catalog["datasets"]}
    if ids and set(ids) - known:
        raise RecordError("Unknown dataset IDs: " + ", ".join(sorted(set(ids) - known)))
    return [d for d in catalog["datasets"] if (not ids or d["id"] in ids)
            and query.lower() in " ".join([d["id"], d.get("title", ""), *d.get("tags", [])]).lower()]


def _archive(dataset: dict, cache: Path, assets_dir: Path | None) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / (dataset["sha256"] + ".asset")
    if path.exists():
        if path.is_symlink() or path.stat().st_size != dataset["size_bytes"] or file_hash(path) != dataset["sha256"]:
            raise RecordError(f"Cached dataset hash mismatch: {path}; remove the corrupt cache entry explicitly")
        return path
    with tempfile.TemporaryDirectory(prefix=".fetch-", dir=cache) as temporary:
        location = dataset["location"]
        source = Path(temporary) / location["asset"]
        if assets_dir:
            shutil.copyfile(assets_dir / location["asset"], source)
        else:
            subprocess.run(["gh", "release", "download", location["release"], "--repo", location["repository"],
                            "--pattern", location["asset"], "--dir", temporary], check=True, capture_output=True)
        if source.stat().st_size != dataset["size_bytes"] or file_hash(source) != dataset["sha256"]:
            raise RecordError("Downloaded dataset hash mismatch: " + location["asset"])
        source.replace(path)
    return path


def _install_file(source: Path, target: Path) -> None:
    """Publish a complete file atomically, without replacing an existing target."""
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".onepiece-restore-", dir=target.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as dst, source.open("rb") as src:
            shutil.copyfileobj(src, dst)
            dst.flush()
            os.fsync(dst.fileno())
        # Both paths are on the destination filesystem. link() fails if a human
        # created the target during the copy and never exposes a partial file.
        os.link(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def fetch_datasets(catalog: dict, destination: Path, *, ids: list[str], cache: Path,
                   assets_dir: Path | None = None, path_prefix: str | None = None) -> dict:
    """Fetch selected datasets and validate every selected byte before installing files."""
    selected = select_datasets(catalog, ids)
    if path_prefix:
        safe_relative(path_prefix.rstrip("/"))
    entries = [(dataset, item) for dataset in selected for item in dataset["files"]
               if not path_prefix or item["path"] == path_prefix or item["path"].startswith(path_prefix.rstrip("/") + "/")]
    if not entries:
        raise RecordError("No files match the dataset selection")
    destination = destination.absolute()
    targets = {}
    missing = []
    for dataset, item in entries:
        target = safe_target(destination, item["path"])
        targets[item["path"]] = target
        if target.exists():
            if not target.is_file() or file_hash(target) != item["sha256"]:
                raise FileExistsError(f"Preserve existing changed file: {target}")
        else:
            missing.append((dataset, item))
    restored = 0
    # Staging is outside the destination; failed checks never leave half-verified files.
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".restore-", dir=cache) as temporary:
        staged = []
        for dataset in selected:
            wanted = [item for d, item in missing if d["id"] == dataset["id"]]
            if not wanted:
                continue
            archive_path = _archive(dataset, cache, assets_dir)
            archive = zipfile.ZipFile(archive_path) if dataset["format"] == "zip" else None
            try:
                if archive:
                    actual = archive.infolist()
                    expected = {f["path"]: f for f in dataset["files"]}
                    if len(actual) != len(expected) or {i.filename for i in actual} != set(expected):
                        raise RecordError("Archive members do not match the dataset manifest")
                    for info in actual:
                        if stat.S_ISLNK(info.external_attr >> 16) or info.file_size != expected[info.filename]["size_bytes"]:
                            raise RecordError("Invalid dataset archive entry")
                for item in wanted:
                    path = Path(temporary) / str(len(staged))
                    checksum = hashlib.sha256()
                    size = 0
                    with (archive.open(item["path"]) if archive else archive_path.open("rb")) as src, path.open("xb") as dst:
                        while chunk := src.read(BLOCK):
                            size += len(chunk)
                            if size > item["size_bytes"]:
                                raise RecordError("Dataset file exceeds its declared size")
                            checksum.update(chunk)
                            dst.write(chunk)
                    if checksum.hexdigest() != item["sha256"] or size != item["size_bytes"]:
                        raise RecordError("Dataset file hash mismatch: " + item["path"])
                    staged.append((path, item))
            finally:
                if archive:
                    archive.close()
        # Recheck targets after downloads; never overwrite edits made while fetching.
        for _, item in staged:
            target = safe_target(destination, item["path"])
            if target.exists():
                raise FileExistsError(f"Destination changed during fetch: {target}")
        for source, item in staged:
            target = safe_target(destination, item["path"])
            _install_file(source, target)
            restored += 1
    return {"ok": True, "catalog_id": catalog["id"], "datasets": [d["id"] for d in selected],
            "verified_files": len(entries), "restored_files": restored, "destination": str(destination)}


def verify_datasets(catalog: dict, destination: Path, *, ids: list[str] | None = None) -> dict:
    errors = []
    count = 0
    for dataset in select_datasets(catalog, ids):
        for item in dataset["files"]:
            path = safe_target(destination.absolute(), item["path"])
            if not path.is_file() or path.stat().st_size != item["size_bytes"] or file_hash(path) != item["sha256"]:
                errors.append(item["path"])
            count += 1
    return {"ok": not errors, "verified_files": count - len(errors), "missing_or_changed": errors}
