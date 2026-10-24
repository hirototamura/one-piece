"""A dataset is reusable evidence only when archive and file hashes both match."""
import copy
import hashlib
import json
from pathlib import Path
import stat
import zipfile

import pytest

from onepiece.cli import main
from onepiece.datasets import fetch_datasets, file_hash, load_catalog, pack_datasets, verify_datasets
from onepiece.model import RecordError


@pytest.fixture
def collection(tmp_path):
    source = tmp_path / "integration-validation"
    (source / "trial").mkdir(parents=True)
    (source / "trial/a.json").write_text('{"score": 0.9}')
    (source / "trial/b.txt").write_text("measured result")
    (source / "trial/index.sqlite").write_text("disposable")
    (source / "receipt.json").write_text('{"physical_verified": false}')
    (source / "trial/symlink").symlink_to(source / "receipt.json")
    with zipfile.ZipFile(source / "legacy.zip", "w") as archive:
        archive.writestr("original.txt", "preserve archive bytes")
    output = tmp_path / "assets"
    result = pack_datasets(source, output, repository="owner/private", release="validation-test", catalog_id="validation-test")
    return source, output, load_catalog(Path(result["catalog"]))


def test_selective_restore_cached_retry_and_original_integrity(collection, tmp_path):
    source, assets, catalog = collection
    destination, cache = tmp_path / "workspace", tmp_path / "cache"
    result = fetch_datasets(catalog, destination, ids=["trial"], cache=cache, assets_dir=assets)
    assert result["restored_files"] == 2
    assert not (destination / "integration-validation/receipt.json").exists()
    assert not (destination / "integration-validation/trial/index.sqlite").exists()
    assert not (destination / "integration-validation/trial/symlink").exists()
    assert verify_datasets(catalog, destination, ids=["trial"])["ok"]
    assert fetch_datasets(catalog, destination, ids=["trial"], cache=cache)["restored_files"] == 0
    # Another environment can reuse the verified cache without network access.
    assert fetch_datasets(catalog, tmp_path / "second", ids=["trial"], cache=cache)["restored_files"] == 2
    assert json.loads((source / "receipt.json").read_text())["physical_verified"] is False
    assert not (destination / ".onepiece").exists()


def test_preserve_existing_edits_before_any_writes(collection, tmp_path):
    _, assets, catalog = collection
    destination = tmp_path / "workspace"
    target = destination / "integration-validation/trial/b.txt"
    target.parent.mkdir(parents=True)
    target.write_text("human edit")
    with pytest.raises(FileExistsError):
        fetch_datasets(catalog, destination, ids=["trial"], cache=tmp_path / "cache", assets_dir=assets)
    assert not target.with_name("a.json").exists()
    assert target.read_text() == "human edit"


def test_archive_and_member_hash_mismatch_leave_no_output(collection, tmp_path):
    _, assets, catalog = collection
    trial = next(d for d in catalog["datasets"] if d["id"] == "trial")
    changed = copy.deepcopy(catalog)
    next(d for d in changed["datasets"] if d["id"] == "trial")["files"][1]["sha256"] = "0" * 64
    with pytest.raises(RecordError, match="file hash mismatch"):
        fetch_datasets(changed, tmp_path / "bad-member", ids=["trial"], cache=tmp_path / "cache", assets_dir=assets)
    assert not (tmp_path / "bad-member").exists()
    (assets / trial["location"]["asset"]).write_bytes(b"corrupt download")
    with pytest.raises(RecordError, match="Downloaded dataset hash mismatch"):
        fetch_datasets(catalog, tmp_path / "bad-archive", ids=["trial"], cache=tmp_path / "uncached", assets_dir=assets)
    assert not (tmp_path / "bad-archive").exists()


@pytest.mark.parametrize("unsafe", ["../escape", "/absolute", "C:/drive", "back\\slash", "a/../escape", "a//b"])
def test_catalog_rejects_unsafe_paths(collection, tmp_path, unsafe):
    _, _, catalog = collection
    catalog["datasets"][0]["files"][0]["path"] = unsafe
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(catalog))
    with pytest.raises(RecordError):
        load_catalog(path)


def test_raw_archives_keep_their_original_bytes_and_prefix_filter(collection, tmp_path):
    source, assets, catalog = collection
    destination = tmp_path / "workspace"
    fetch_datasets(catalog, destination, ids=["archive-legacy.zip"], cache=tmp_path / "cache", assets_dir=assets)
    assert file_hash(source / "legacy.zip") == file_hash(destination / "integration-validation/legacy.zip")
    assert not (destination / "original.txt").exists()  # Raw archive is evidence, never implicitly executed/extracted.
    fetch_datasets(catalog, destination, ids=["trial"], path_prefix="integration-validation/trial/a.json", cache=tmp_path / "cache", assets_dir=assets)
    assert (destination / "integration-validation/trial/a.json").exists()
    assert not (destination / "integration-validation/trial/b.txt").exists()


def test_fetch_rejects_existing_symlink_and_catalogued_zip_symlink(collection, tmp_path):
    _, assets, catalog = collection
    destination = tmp_path / "workspace"
    destination.mkdir()
    (destination / "integration-validation").symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(RecordError, match="symlink"):
        fetch_datasets(catalog, destination, ids=["trial"], cache=tmp_path / "cache", assets_dir=assets)
    trial = next(d for d in catalog["datasets"] if d["id"] == "trial")
    archive_path = assets / trial["location"]["asset"]
    with zipfile.ZipFile(archive_path, "w") as z:
        for item in trial["files"]:
            info = zipfile.ZipInfo(item["path"])
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            z.writestr(info, "a" * item["size_bytes"])
    trial.update(sha256=file_hash(archive_path), size_bytes=archive_path.stat().st_size)
    with pytest.raises(RecordError, match="Invalid dataset archive entry"):
        fetch_datasets(catalog, tmp_path / "second", ids=["trial"], cache=tmp_path / "cache2", assets_dir=assets)


def test_list_cli_needs_neither_network_nor_record_store(collection, tmp_path, monkeypatch, capsys):
    _, assets, _ = collection
    monkeypatch.chdir(tmp_path)
    assert main(["datasets", "list", str(assets / "catalog.json"), "--query", "trial"]) == 0
    assert [d["id"] for d in json.loads(capsys.readouterr().out)["datasets"]] == ["trial"]
    assert not (tmp_path / ".onepiece").exists()


def test_primary_sqlite_data_is_archived_while_disposable_index_is_excluded(collection, tmp_path):
    source, _, _ = collection
    raw = b"SQLite format 3\x00primary experimental measurements"
    (source / "trial/measurements.sqlite").write_bytes(raw)
    assets = tmp_path / "raw-data-assets"
    packed = pack_datasets(source, assets, repository="owner/private", release="raw-data", catalog_id="raw-data")
    catalog = load_catalog(Path(packed["catalog"]))
    trial = next(d for d in catalog["datasets"] if d["id"] == "trial")
    assert any(f["path"].endswith("measurements.sqlite") for f in trial["files"])
    assert not any(f["path"].endswith("index.sqlite") for f in trial["files"])
    destination = tmp_path / "raw-data-restore"
    fetch_datasets(catalog, destination, ids=["trial"], cache=tmp_path / "cache", assets_dir=assets)
    assert (destination / "integration-validation/trial/measurements.sqlite").read_bytes() == raw


def test_parent_file_conflict_stops_before_download_or_partial_install(collection, tmp_path):
    _, assets, catalog = collection
    destination = tmp_path / "workspace"
    destination.mkdir()
    (destination / "integration-validation").write_text("existing human data")
    with pytest.raises(FileExistsError, match="non-directory parent"):
        fetch_datasets(catalog, destination, ids=["trial"], cache=tmp_path / "cache", assets_dir=assets)
    assert not (tmp_path / "cache").exists()
    assert (destination / "integration-validation").read_text() == "existing human data"
