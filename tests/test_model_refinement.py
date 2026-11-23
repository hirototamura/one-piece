import copy
import json
import runpy
import shutil
import subprocess
from pathlib import Path

import pytest

from onepiece import Store
from onepiece._explorer_projection import project_model
from onepiece.model import canonical_bytes, digest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def refinement():
    module = runpy.run_path(str(ROOT / "projects/balancing-cube/refine_model.py"))
    history = module["load_records"](ROOT / "projects/balancing-cube/store")
    before = canonical_bytes(history)
    updates = module["build_refinement"](history)
    assert canonical_bytes(history) == before
    return module, history, updates


def test_eight_corner_mission_and_planned_case_share_the_new_acceptance(refinement):
    _, _, updates = refinement
    current = {r["id"]: r for r in updates}
    mission = current["M-VERTEX"]["data"]
    case = current["cube.verify.M-VERTEX"]["data"]
    assert mission["statement"] == "The Cube shall balance on each of its 8 corners with its 3 reaction wheels."
    assert mission["acceptance_criteria"] == case["acceptance_criteria"] == {
        "domain": "hardware", "metric": "distinct_corners_demonstrated", "operator": "==", "unit": "count", "value": 8,
    }
    assert mission["verification_status"] == case["execution_status"] == "not_run"
    assert case["evidence_refs"] == []
    assert sum(r["kind"] == "requirement" and r["data"]["record_role"] == "requirement_group" for r in updates) == 7
    assert sum(r["kind"] == "requirement" and r["data"]["record_role"] == "requirement" for r in updates) == 22


def test_kdp_references_are_exact_atomic_inverses_of_the_recorded_edges(refinement):
    module, history, updates = refinement
    by_ref = {(r["id"], r["revision"]): r for r in history + updates}
    reqs = [r for r in updates if r["kind"] == "requirement"]
    params = [r for r in updates if r["kind"] == "parameter"]
    changed = []
    assert len(params) == 37
    for p in params:
        expected = {r["id"] for r in reqs if any(e["type"] == "constrain" and e["target"]["id"] == p["id"] for e in r["links"])}
        assert set(p["data"]["requirements"]) == expected
        assert all(by_ref[x["id"], x["revision"]]["data"]["record_role"] == "requirement" for x in p["data"]["requirement_refs"])
        old = by_ref[p["id"], module["SOURCE_REVISION"]]["data"]
        if set(old["requirements"]) != expected:
            changed.append(p["id"])
        for key in ("value", "unit", "origin", "bounds", "standard_uncertainty", "model_path", "role"):
            assert p["data"].get(key) == old.get(key)
    assert len(changed) == 14


def test_refinement_preserves_physics_and_records_a_policy_without_enabling_code_execution(refinement):
    module, history, updates = refinement
    old = {(r["id"], r["revision"]): r for r in history}
    snapshot = next(r for r in updates if r["kind"] == "simulation_snapshot")
    source = old[snapshot["id"], module["SOURCE_REVISION"]]
    for key in ("model", "controller", "contract", "plan", "families", "physical_fidelity", "comparison_design_ref"):
        assert snapshot["data"].get(key) == source["data"].get(key)
    policy = snapshot["data"]["change_contract"]
    assert policy["allowed_repository"] == "balancing-cube-simulation"
    assert policy["allowed_path"] == "balancing_cube/control.py"
    assert policy["algorithm_proposal_execution_implemented"] is False
    assert "screening and scoring" in policy["fixed_boundaries"]


def test_refinement_is_idempotent_and_baseline_and_configuration_hashes_resolve(refinement):
    module, history, updates = refinement
    assert canonical_bytes(module["build_refinement"](history + updates)) == canonical_bytes(updates)
    rows = {(r["id"], r["revision"]): r for r in history + updates}
    Store._check_references(rows.values())
    baseline = next(r for r in updates if r["kind"] == "baseline")
    assert all(digest(rows[x["id"], x["revision"]]) == x["sha256"] for x in baseline["data"]["members"])
    cm = next(r for r in updates if r["id"] == "cube.configuration.cm-01")
    snapshot_ref = cm["data"]["snapshot_ref"]
    assert cm["data"]["snapshot_record_sha256"] == digest(rows[snapshot_ref["id"], snapshot_ref["revision"]])
    projection = project_model(rows, next(r for r in updates if r["kind"] == "system_model"))
    cube = projection["balancing_cube"]
    assert cube["counts"]["linked_kdps"] == 37
    assert len(cube["reviewed_architecture"]["components"]) == 10
    assert next(p for p in cube["kdps"] if p["id"] == "D-SIDE")["requirement_refs"]


@pytest.mark.skipif(not shutil.which("node"), reason="Node is required for the explorer graph regression")
def test_graph_connects_parameters_to_exact_requirements_without_group_fallback(refinement, tmp_path):
    _, history, updates = refinement
    rows = {(r["id"], r["revision"]): r for r in history + updates}
    model = next(r for r in updates if r["kind"] == "system_model")
    data = project_model(rows, model)
    data["balancing_cube"]["architecture_draft"] = {"status": "unavailable"}
    # A stale display label must not invent an extra group-to-KDP graph edge.
    next(p for p in data["balancing_cube"]["kdps"] if p["id"] == "D-SIDE")["requirements"] = ["C-FIT"]
    path = tmp_path / "model.json"
    path.write_text(json.dumps(data))
    script = r"""
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const context = vm.createContext({fetch: () => new Promise(() => {}), console});
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
vm.runInContext('DATA = ' + fs.readFileSync(process.argv[2], 'utf8') + '; architectureMode = "recorded";', context);
const related = JSON.parse(vm.runInContext('JSON.stringify(graphEdgesFor("D-SIDE"))', context));
assert(related.some(e => e.type === 'constrain' && e.source === 'C-FIT-PRINT'));
assert(related.some(e => e.type === 'constrain' && e.source === 'R-HOLD'));
assert(!related.some(e => e.type === 'constrain' && e.source === 'C-FIT'));
assert(related.filter(e => e.type === 'constrain').every(e => e.sourceRevision && e.targetRevision));
assert.equal(vm.runInContext('graphNode("D-SIDE").kind', context), 'design_parameter');
"""
    subprocess.run(["node", "-e", script, str(ROOT / "src/onepiece/explorer_assets/app.js"), str(path)], check=True)
