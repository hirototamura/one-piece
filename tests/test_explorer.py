"""Browser projections retain exact model references, approval states and claim scope."""
import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from onepiece import Store, make_record, ref
from onepiece.explorer import build_explorer
from onepiece._explorer_claims import project_claims
from onepiece.model import canonical_bytes

ROOT = Path(__file__).resolve().parents[1]


def test_reviewed_cube_build_is_portable_and_preserves_canonical_text(tmp_path):
    store = Store(ROOT / "projects/balancing-cube/store")
    result = build_explorer(store, tmp_path / "explorer", revision="reviewed-20261019-1")
    assert result["counts"] == {"obligations": 22, "groups": 7, "verification_cases": 22, "linked_kdps": 37}
    models = json.loads((tmp_path / "explorer/data/models.json").read_text())
    records = {(r["id"], r["revision"]): r for r in store.records("balancing-cube")}
    for r in models["balancing_cube"]["requirements"]:
        canonical = records[(r["id"], r["revision"])]["data"]
        assert r["statement"] == canonical["statement"]
        assert r["approval_state"] == canonical["approval_state"]
        assert r["physical_verified"] == canonical["physical_verified"]
    assert models["eclss"] is None and models["scrubber"] is None
    provenance = models["generated_from"]
    assert provenance["snapshot_ref"] == {"id": "cube.simulation.snapshot", "revision": "reviewed-20261019-1"}
    assert "/Users/" not in json.dumps(provenance)
    assert json.loads((tmp_path / "explorer/data/cube-architecture-draft.json").read_text())["status"] == "unavailable"
    assert build_explorer(store, tmp_path / "explorer", revision="reviewed-20261019-1") == result


def minimal_records(project):
    def record(id, kind, data, revision="1", date="2026-10-19T00:00:00+00:00"):
        return make_record(project_id=project, id=id, kind=kind, revision=revision, data=data,
                           product_node="cube.system", created_at=date)
    product = record("cube.system", "product", {"name": "Cube"})
    requirement = record("R-1", "requirement", {"name": "One obligation", "statement": "The cube shall hold.", "record_role": "requirement_statement"})
    snapshot = record("snapshot", "simulation_snapshot", {"context_refs": {"requirements": [ref(requirement)], "products": [ref(product)]}})
    model = record("cube.system-model.active", "system_model", {"simulation_snapshot_ref": ref(snapshot), "approval_state": "draft"})
    newer = record("cube.system-model.active", "system_model", {"simulation_snapshot_ref": ref(snapshot), "approval_state": "pending_human_review"}, revision="2", date="2026-10-20T00:00:00+00:00")
    return [product, requirement, snapshot, model, newer]


def test_model_selection_is_explicit_and_project_scoped(tmp_path):
    store = Store(tmp_path / "store")
    source = minimal_records("wanted")
    collision = minimal_records("other")
    collision[1]["data"]["statement"] = "Another project's statement."
    store.import_records(source + collision)
    result = build_explorer(store, tmp_path / "latest", project_id="wanted")
    assert result["model_ref"]["revision"] == "2"
    result = build_explorer(store, tmp_path / "pinned", project_id="wanted", revision="1")
    assert result["model_ref"]["revision"] == "1"
    data = json.loads((tmp_path / "pinned/data/models.json").read_text())
    assert data["balancing_cube"]["model"]["approval_state"] == "draft"
    assert data["balancing_cube"]["requirements"][0]["statement"] == source[1]["data"]["statement"]
    assert "reviewed_architecture" not in data["balancing_cube"]


def test_explorer_does_not_write_into_canonical_store(tmp_path):
    store = Store(tmp_path / "store")
    store.import_records(minimal_records("wanted"))
    with pytest.raises(ValueError, match="outside the canonical store"):
        build_explorer(store, store.path / "explorer", project_id="wanted")


def test_historical_claims_survive_multiple_reviews_without_becoming_current(tmp_path):
    store = Store(ROOT / "projects/balancing-cube/store")
    historical = []
    for revision in ("reviewed-20261019-1", "refined-20261115-1", "requirements-review-20261115-3"):
        output = tmp_path / revision
        build_explorer(store, output, revision=revision)
        claims = json.loads((output / "data/design-claims.json").read_text())
        assert claims["designs"] == []
        historical.append(claims["historical_designs"])
    assert historical[0]
    assert canonical_bytes(historical[0]) == canonical_bytes(historical[1]) == canonical_bytes(historical[2])
    assert any(d["numerical_results"] for d in historical[2])
    records = {(r["id"], r["revision"]): r for r in store.records("balancing-cube")}
    projection = json.loads((tmp_path / "requirements-review-20261115-3/data/models.json").read_text())
    unrelated = copy.deepcopy(next(iter(historical[2]))["source_record"])
    unrelated.update(id="unrelated-candidate", revision="1")
    unrelated["links"] = [{"type": "satisfy", "target": {"id": "R-TILT", "revision": "unrelated-branch"}}]
    records[unrelated["id"], unrelated["revision"]] = unrelated
    filtered = project_claims(records, projection)
    assert "unrelated-candidate" not in {d["id"] for d in filtered["historical_designs"]}


@pytest.mark.skipif(not shutil.which("node"), reason="Node is required for the browser-render regression")
def test_historical_model_without_approval_state_renders_unknown_label(tmp_path):
    output = tmp_path / "historical"
    build_explorer(Store(ROOT / "projects/balancing-cube/store"), output, revision="trace-20261010-2")
    script = r"""
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const nodes = new Map();
const context = vm.createContext({fetch: () => new Promise(() => {}), console,
  document: {querySelector: selector => {
    if (!nodes.has(selector)) nodes.set(selector, {});
    return nodes.get(selector);
  }}});
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
vm.runInContext('DATA = ' + fs.readFileSync(process.argv[2], 'utf8') + '; renderCubeStats();', context);
assert.match(nodes.get('#model-revision').textContent, /trace-20261010-2.*not recorded/i);
assert(nodes.get('#cube-stats').innerHTML.includes('SYSTEM REQUIREMENTS'));
"""
    subprocess.run(["node", "-e", script, str(output / "app.js"), str(output / "data/models.json")], check=True)
