import hashlib
import json
import sqlite3
import zipfile
from pathlib import Path

import pytest

from onepiece import ConflictError, IntegrityError, RecordError, Store, make_record, ref
from onepiece.store import file_sha256


def record(id="req.balance", kind="requirement", **kw):
    return make_record(project_id="cube", id=id, kind=kind, created_at="2026-10-09T13:00:00+00:00", **kw)


def test_import_is_atomic_idempotent_and_revisions_are_immutable(tmp_path):
    store = Store(tmp_path / "store")
    requirement = record(data={"success_criteria": {"tilt": {"max": 5, "unit": "deg"}}})
    design = record("design.a", "design", links=[{"type": "satisfy", "target": ref(requirement)}])
    assert store.import_records([design, requirement])["imported"] == 2
    assert store.import_records([requirement, design])["unchanged"] == 2
    conflicting = json.loads(json.dumps(requirement))
    conflicting["data"]["success_criteria"]["tilt"]["max"] = 20
    with pytest.raises(ConflictError):
        store.import_records([record("new"), conflicting])
    assert len(store.records()) == 2
    dangling = record("dangling", "evidence", links=[{"type": "verify", "target": ref("missing", "1")}])
    with pytest.raises(IntegrityError, match="Dangling"):
        store.import_records([record("also-new"), dangling])
    assert len(store.records()) == 2
    assert store.check()["ok"]


def test_typed_graph_directions_and_derive_cycles(tmp_path):
    store = Store(tmp_path)
    requirement, design = record(), record("design", "design")
    invalid = record("bad", "requirement", links=[{"type": "verify", "target": ref(design)}])
    with pytest.raises(IntegrityError, match="Invalid verify direction"):
        store.import_records([requirement, design, invalid])
    a = record("a", links=[{"type": "derive", "target": ref("b", "1")}])
    b = record("b", links=[{"type": "derive", "target": ref("a", "1")}])
    with pytest.raises(IntegrityError, match="Cycle"):
        store.import_records([a, b])
    assert store.records() == []


def test_missing_or_bad_artifact_does_not_publish_batch(tmp_path):
    store = Store(tmp_path / "store")
    source = tmp_path / "inputs"
    source.mkdir()
    (source / "trial.json").write_text('{"tilt": 2.0}')
    sha = file_sha256(source / "trial.json")
    evidence = record("ev", "evidence", artifacts=[{"path": "trial.json", "sha256": sha, "size_bytes": 999}])
    # Incorrect size is a material evidence-integrity failure.
    with pytest.raises(IntegrityError, match="size mismatch"):
        store.import_records([record(), evidence], artifacts_root=source)
    assert store.records() == []
    evidence["artifacts"][0]["size_bytes"] = (source / "trial.json").stat().st_size
    store.import_records([record(), evidence], artifacts_root=source)
    (source / "trial.json").unlink()
    assert store.check()["ok"]
    store.artifact_path(evidence["artifacts"][0]).write_text("tampered")
    assert not store.check()["ok"]


def test_existing_artifact_size_is_checked_before_publishing_new_record(tmp_path):
    content = b"shared evidence bytes"
    sha = hashlib.sha256(content).hexdigest()
    store = Store(tmp_path / "store")
    artifact = {"path": "result", "sha256": sha, "size_bytes": len(content)}
    store.import_records([record("original", "evidence", artifacts=[artifact])],
                         artifact_objects={sha: content})
    before = store.records()
    bad = record("reused", "evidence", artifacts=[{**artifact, "size_bytes": len(content) + 1}])
    with pytest.raises(IntegrityError, match="size mismatch"):
        store.import_records([record("also-new"), bad])
    assert store.records() == before
    assert store.check()["ok"]


def test_traversal_and_escaping_symlink_artifacts_are_rejected(tmp_path):
    for name in ["../outside", "/etc/passwd", "C:/secret", "a\\b", "a/./b", "a//b"]:
        with pytest.raises(RecordError):
            record("ev", "evidence", artifacts=[{"path": name, "sha256": "a" * 64}])
    source = tmp_path / "inputs"
    source.mkdir()
    outside = tmp_path / "outside"
    outside.write_bytes(b"secret")
    (source / "link").symlink_to(outside)
    evidence = record("ev", "evidence", artifacts=[{"path": "link", "sha256": file_sha256(outside)}])
    with pytest.raises(IntegrityError):
        Store(tmp_path / "store").import_records([evidence], artifacts_root=source)


def test_sqlite_is_rebuildable_from_canonical_json(tmp_path):
    store = Store(tmp_path)
    store.import_records([record()])
    store.index_path.unlink()
    rebuilt = Store(tmp_path)
    assert rebuilt.records()[0]["id"] == "req.balance"
    assert rebuilt.check()["ok"]
    commit = next(p for p in rebuilt.commits.iterdir() if not p.name.startswith("."))
    records = json.loads((commit / "records.json").read_text())
    records[0]["data"]["tampered"] = True
    (commit / "records.json").write_text(json.dumps(records))
    assert not rebuilt.check()["ok"]


def test_context_preserves_all_units_uncertainty_and_bounds_evidence(tmp_path):
    store = Store(tmp_path)
    requirements = [record("req." + str(i)) for i in range(3)]
    parameter = record("kdp.mass", "parameter", product_node="system/mechanics", data={"value": 0.7, "unit": "kg", "uncertainty": {"type": "assumed", "range": [0.6, 0.9]}})
    snapshot = record("snapshot", "simulation_snapshot", data={"model": {"timestep_s": 0.001}})
    evidence = [record("ev." + str(i), "evaluation") for i in range(8)]
    store.import_records(requirements + [parameter, snapshot] + evidence)
    context = store.context("cube", product_node="system/control", max_evidence=1)
    assert {r["id"] for r in context["records"]} == {r["id"] for r in requirements + [parameter, snapshot]}
    context = store.context("cube", max_evidence=2)
    assert sum(r["kind"] == "evaluation" for r in context["records"]) == 2
    assert next(r for r in context["records"] if r["id"] == "kdp.mass")["data"] == parameter["data"]


def test_bundle_roundtrip_hash_and_zip_safety(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "result.txt").write_text("actual data")
    store = Store(tmp_path / "original")
    evidence = record("evidence", "evidence", artifacts=[{"path": "result.txt", "sha256": file_sha256(source / "result.txt")}])
    store.import_records([record(), evidence], artifacts_root=source)
    bundle = store.bundle(tmp_path / "release.zip")
    restored = Store(tmp_path / "restored")
    assert restored.fetch(Path(bundle["path"]).as_uri(), expected_sha256=bundle["sha256"])["imported"] == 2
    assert restored.records() == store.records()
    assert restored.import_bundle(bundle["path"], expected_sha256=bundle["sha256"])["unchanged"] == 2
    with pytest.raises(IntegrityError, match="SHA-256"):
        restored.import_bundle(bundle["path"], expected_sha256="0" * 64)
    malicious = tmp_path / "malicious.zip"
    with zipfile.ZipFile(malicious, "w") as z:
        z.writestr("../escape", "bad")
    with pytest.raises(RecordError):
        restored.import_bundle(malicious, expected_sha256=file_sha256(malicious))
    assert not (tmp_path / "escape").exists()


def test_bundle_roundtrip_for_highly_compressible_artifact_and_manifest(tmp_path):
    content = bytes(1024 * 1024)
    sha = hashlib.sha256(content).hexdigest()
    store = Store(tmp_path / "original")
    ev = record("zeros", "evidence", data={"repeated": "0" * 1024 * 1024},
                artifacts=[{"path": "zeros.bin", "sha256": sha, "size_bytes": len(content)}])
    store.import_records([ev], artifact_objects={sha: content})
    bundle = store.bundle(tmp_path / "release.zip")
    with zipfile.ZipFile(bundle["path"]) as archive:
        assert all(info.compress_type == zipfile.ZIP_STORED for info in archive.infolist())
    clone = Store(tmp_path / "clone")
    clone.import_bundle(bundle["path"], expected_sha256=bundle["sha256"])
    assert clone.records() == [ev]
    assert clone.artifact_path(ev["artifacts"][0]).read_bytes() == content
    assert clone.check()["ok"]
    unsafe = tmp_path / "overcompressed.zip"
    with zipfile.ZipFile(unsafe, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("bundle.json", bytes(1024 * 1024))
    with pytest.raises(IntegrityError, match="expansion ratio"):
        clone.import_bundle(unsafe, expected_sha256=file_sha256(unsafe))


def test_project_check_and_bundle_require_only_that_projects_artifacts(tmp_path):
    store = Store(tmp_path / "store")
    artifacts = {}
    records = []
    for project in ("a", "b"):
        content = project.encode()
        sha = hashlib.sha256(content).hexdigest()
        artifacts[sha] = content
        records.append(make_record(project_id=project, id="ev", kind="evidence",
                                   artifacts=[{"path": "result", "sha256": sha, "size_bytes": len(content)}]))
    store.import_records(records, artifact_objects=artifacts)
    store.artifact_path(records[1]["artifacts"][0]).unlink()
    assert not store.check()["ok"]
    assert not store.check("b")["ok"]
    assert store.check("a")["ok"]
    bundle = store.bundle(tmp_path / "a.zip", "a")
    clone = Store(tmp_path / "clone")
    clone.import_bundle(bundle["path"], expected_sha256=bundle["sha256"])
    assert clone.records() == [records[0]]
    assert clone.check()["ok"]


def test_no_numerical_physical_pass_or_agent_baseline(tmp_path):
    with pytest.raises(RecordError, match="physical validation"):
        record("lie", "evidence", data={"evidence_type": "simulation", "physical_validation": True})
    with pytest.raises(RecordError, match="human"):
        record("baseline", "baseline")
    store = Store(tmp_path)
    store.import_records([record()])
    with pytest.raises(RecordError):
        store.baseline("cube", id="b1", actor={"type": "agent", "id": "optimizer"}, reason="automatic")
    assert store.baseline("cube", id="b1", actor={"type": "human", "id": "test-user"}, reason="configuration reviewed")["imported"] == 1
    assert store.records(kinds=["baseline"])[0]["data"]["scope"] == "configuration_identity_only_not_physical_acceptance"


def test_ref_requires_revision_and_finite_json():
    with pytest.raises(RecordError):
        ref("req.balance")
    with pytest.raises(RecordError):
        record(data={"measurement": float("nan")})


def test_record_schema_accepts_real_envelope():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((Path(__file__).parents[1] / "schemas" / "record.schema.json").read_text())
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(record())


def test_baseline_members_pin_real_revision_hashes_atomically(tmp_path):
    from onepiece.model import digest
    store = Store(tmp_path)
    requirement = record()
    store.import_records([requirement])
    base = record("base", "baseline", actor={"type": "human", "id": "reviewer"}, data={"reason": "reviewed", "members": [{**ref(requirement), "sha256": "0" * 64}]})
    with pytest.raises(IntegrityError, match="member digest"):
        store.import_records([record("must-not-commit"), base])
    assert len(store.records()) == 1
    base["data"]["members"][0] = {"id": "missing", "revision": "1", "sha256": digest(requirement)}
    with pytest.raises(IntegrityError, match="Dangling baseline"):
        store.import_records([base])
    base["data"]["members"][0] = {**ref(requirement), "sha256": digest(requirement)}
    store.import_records([base])
    assert store.check()["ok"]


def test_packaged_schema_matches_source_and_unknown_fields_are_preserved(tmp_path):
    from onepiece import record_schema
    source = json.loads((Path(__file__).parents[1] / "schemas" / "record.schema.json").read_text())
    assert record_schema() == source
    envelope = record()
    envelope["extension"] = {"team": "mechanics"}
    Store(tmp_path).import_records([envelope])
    assert Store(tmp_path).records()[0]["extension"] == envelope["extension"]


def test_index_contents_cannot_override_canonical_records(tmp_path):
    store = Store(tmp_path)
    store.import_records([record(data={"meaning": "canonical"})])
    with sqlite3.connect(store.index_path) as db:
        fake = record(data={"meaning": "fake index body"})
        db.execute("UPDATE records SET body=?", (json.dumps(fake),))
        db.commit()
    assert store.records()[0]["data"]["meaning"] == "canonical"


def test_physical_verified_alias_cannot_promote_simulation():
    with pytest.raises(RecordError, match="physical validation"):
        record("not-hardware", "evaluation", data={"physical_verified": True, "claim_scope": "simulation"})


def test_bundle_missing_objects_and_symlink_entries_rejected(tmp_path):
    store = Store(tmp_path / "store")
    envelope = record("ev", "evidence", artifacts=[{"path": "measurement", "sha256": "a" * 64}])
    bundle = tmp_path / "missing.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("bundle.json", json.dumps({"schema_version": "1.0", "format": "onepiece-evidence-bundle", "records": [envelope]}))
    with pytest.raises(IntegrityError, match="artifact set"):
        store.import_bundle(bundle, expected_sha256=file_sha256(bundle))
    assert store.records() == []
    bundle = tmp_path / "link.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        info = zipfile.ZipInfo("objects/" + "a" * 64)
        info.create_system = 3
        info.external_attr = 0o120777 << 16
        archive.writestr(info, "../elsewhere")
    with pytest.raises(IntegrityError, match="Unsafe ZIP"):
        store.import_bundle(bundle, expected_sha256=file_sha256(bundle))


def test_cli_import_context_and_required_zip_hash(tmp_path, capsys):
    from onepiece.cli import main
    source = tmp_path / "records.json"
    source.write_text(json.dumps([record()]))
    args = ["--store", str(tmp_path / "store")]
    assert main(args + ["import", str(source)]) == 0
    assert main(args + ["context", "--project", "cube", "--max-designs", "0", "--max-evidence", "0"]) == 0
    assert main(args + ["check"]) == 0
    fake_zip = tmp_path / "evidence.zip"
    assert main(args + ["import", str(fake_zip)]) == 2
    assert "require --sha256" in capsys.readouterr().err


def test_bundle_rehydrates_metadata_only_clone_without_rewriting_records(tmp_path):
    import shutil
    source = tmp_path / "source"
    source.mkdir()
    (source / "result").write_text("measured experiment bytes")
    original = Store(tmp_path / "original")
    ev = record("ev", "evidence", artifacts=[{"path": "result", "sha256": file_sha256(source / "result")}])
    original.import_records([record(), ev], artifacts_root=source)
    bundle = original.bundle(tmp_path / "release.zip")
    clone_root = tmp_path / "clone"
    shutil.copytree(original.path, clone_root, ignore=shutil.ignore_patterns("objects", "index.sqlite", ".write.lock"))
    clone = Store(clone_root)
    assert len(clone.records()) == 2
    assert not clone.check()["ok"]
    before = clone.records()
    result = clone.import_bundle(bundle["path"], expected_sha256=bundle["sha256"])
    assert result["imported"] == 0 and result["unchanged"] == 2 and result["restored_artifacts"] == 1
    assert clone.records() == before
    assert clone.check()["ok"]
    assert clone.import_bundle(bundle["path"], expected_sha256=bundle["sha256"])["commit_id"] is None
    # Git retains the objects-only restore commit's metadata, but excludes its
    # objects. Re-cloning and restoring must work repeatedly, not just once.
    for generation in range(2):
        clone_root = tmp_path / f"clone-{generation + 2}"
        shutil.copytree(clone.path, clone_root, ignore=shutil.ignore_patterns("objects", "index.sqlite", ".write.lock"))
        clone = Store(clone_root)
        canonical = {str(p.relative_to(clone.path)): p.read_bytes()
                     for p in clone.commits.rglob("*.json")}
        assert not clone.check()["ok"]
        restored = clone.import_bundle(bundle["path"], expected_sha256=bundle["sha256"])
        assert restored["imported"] == 0 and restored["restored_artifacts"] == 1
        assert clone.check()["ok"] and clone.records() == before
        assert canonical == {str(p.relative_to(clone.path)): p.read_bytes()
                             for p in clone.commits.rglob("*.json")}
        assert clone.import_bundle(bundle["path"], expected_sha256=bundle["sha256"])["commit_id"] is None


def test_index_filter_columns_cannot_hide_canonical_requirements(tmp_path):
    store = Store(tmp_path)
    store.import_records([record()])
    with sqlite3.connect(store.index_path) as db:
        db.execute("UPDATE records SET kind='design'")
        db.commit()
    assert len(store.records(kinds=["requirement"])) == 1


def test_scoped_context_keeps_all_parameters_and_exact_snapshot(tmp_path):
    store = Store(tmp_path)
    old = record("snapshot", "simulation_snapshot", revision="1", data={"model": {"mass": 1}})
    current = record("snapshot", "simulation_snapshot", revision="2", data={"model": {"mass": 2}})
    run = record("run.snapshot", "simulation_snapshot", data={"model": {"mass": 2}})
    param = record("mass", "parameter", data={"value": 2, "unit": "kg", "standard_uncertainty": None})
    store.import_records([record(), old, current, run, param])
    context = store.context("cube", kinds=["evidence"], snapshot_ref=ref(current), max_designs=0, max_evidence=0)
    assert [r for r in context["records"] if r["kind"] == "simulation_snapshot"] == [current]
    assert param in context["records"] and record() in context["records"]
    assert context["omitted_record_count"] == 2 and context["snapshot_ref"] == ref(current)
    with pytest.raises(RecordError, match="existing exact revision"):
        store.context("cube", snapshot_ref={"id": "snapshot", "revision": "missing"})


def test_scoped_context_pins_comparison_and_campaign_outside_limits(tmp_path):
    store = Store(tmp_path)
    best = record("D-best", "design")
    summary = record("campaign", "campaign_summary", data={"prior46": {"status_counts": {"pass": 31, "fail": 9, "inconclusive": 6}}})
    snapshot = record("snapshot", "simulation_snapshot", data={"comparison_design_ref": ref(best)})
    newer = [make_record(project_id="cube", id=f"test-{i}", kind="design_candidate") for i in range(7)]
    iteration = record("legacy", "iteration", data={"best_design_ref": ref(best), "other_ref": ref("omitted", "1")})
    omitted = record("omitted", "design")
    store.import_records([best, summary, snapshot, iteration, omitted, *newer])
    context = store.context("cube", kinds=["design_candidate", "iteration"], max_designs=5, max_evidence=0, snapshot_ref=ref(snapshot))
    assert best in context["records"] and summary in context["records"]
    assert len([r for r in context["records"] if r["kind"] == "design_candidate"]) == 5
    assert context["counts"]["pinned_designs"] == 1
    assert any(r["type"] == "data_reference" and r["target"] == ref(omitted) for r in context["omitted_references"])


def test_context_pins_requirement_revision_and_does_not_mix_superseded_trace(tmp_path):
    store = Store(tmp_path)
    old = record("mission", data={"owner": "old"})
    new = make_record(project_id="cube", id="mission", kind="requirement", revision="2", data={"owner": "system"})
    snapshot = record("snapshot", "simulation_snapshot", data={"context_refs": {"requirements": [ref(old)]}})
    store.import_records([old, new, snapshot])
    context = store.context("cube", snapshot_ref=ref(snapshot))
    assert old in context["records"] and new not in context["records"]
