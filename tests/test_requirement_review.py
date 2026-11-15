import json
import runpy
from pathlib import Path

import pytest

from onepiece import Store
from onepiece._explorer_projection import project_model
from onepiece.model import canonical_bytes
from onepiece.store import current_records

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def review():
    load = runpy.run_path(str(ROOT / "projects/balancing-cube/refine_model.py"))["load_records"]
    module = runpy.run_path(str(ROOT / "projects/balancing-cube/apply_requirement_review.py"))
    history = load(ROOT / "projects/balancing-cube/store")
    before = canonical_bytes(history)
    changes = module["build_review"](history)
    assert before == canonical_bytes(history)
    return module, history, changes


def test_comments_preserve_mandatory_requirements_and_separate_constraints(review):
    _, history, changes = review
    current = {r["id"]: r for r in changes}
    reqs = [r for r in changes if r["kind"] == "requirement" and r["data"].get("record_role") == "requirement" and r["data"].get("status") != "retired"]
    assert len(reqs) == 19
    assert {r["id"] for r in changes if r["kind"] == "constraint"} == {"C-BUDGET", "C-FIT-PRINT", "C-JAPAN"}
    assert all(current[id]["kind"] == "requirement" for id in ["M-VERTEX", "R-HOLD", "R-REPEAT", "C-FIT-INSTALL", "C-PRINT", "R-VISION"])
    assert current["C-FIT-MATERIAL"]["data"]["status"] == "retired"
    assert current["C-BUDGET"]["data"]["constraint_scope"] == "project"
    assert current["C-FIT-PRINT"]["data"]["constraint_scope"] == "manufacturing"
    assert all(e["target"]["id"] != "D-SIDE" for e in current["C-FIT-PRINT"]["links"])


def test_hold_interval_is_a_shared_operating_value_not_a_new_search_kdp(review):
    _, _, changes = review
    current = {r["id"]: r for r in changes}
    snapshot = current["cube.simulation.snapshot"]["data"]
    assert current["O-HOLD-INTERVAL"]["data"]["value"] == 10
    assert current["O-HOLD-INTERVAL"]["data"]["role"] == "operating"
    assert current["R-HOLD"]["data"]["acceptance_criteria"]["value"] == 10
    assert current["cube.verify.R-HOLD"]["data"]["acceptance_criteria"]["value"] == 10
    for id in ["R-HOLD", "R-REPEAT", "R-DRIFT", "R-RMS", "R-TILT", "R-YAW"]:
        assert current[id]["data"]["hold_interval_ref"]["id"] == "O-HOLD-INTERVAL"
        assert not any("30 s" in text for text in current[id]["data"].get("conditions", []))
    assert len(snapshot["context_refs"]["kdps"]) == 37
    assert "O-HOLD-INTERVAL" not in {x["id"] for x in snapshot["context_refs"]["kdps"]}
    assert current["R-REPEAT"]["data"]["acceptance_criteria"]["value"] == 9


def test_derivation_paths_and_configuration_management_ownership(review):
    _, _, changes = review
    current = {r["id"]: r for r in changes}
    for id in ["R-DRIFT", "R-RMS", "R-TILT"]:
        assert {e["target"]["id"] for e in current[id]["links"] if e["type"] == "derive"} == {"M-VERTEX"}
    for id in ["R-DRIVE-CURRENT", "R-DRIVE-SPEED", "R-DRIVE-TEMP", "R-DRIVE-TORQUE", "R-DRIVE-VOLTAGE", "R-MODEL", "R-SYNC"]:
        assert {e["target"]["id"] for e in current[id]["links"] if e["type"] == "derive"} == {"R-TILT", "R-RMS"}
    assert {e["target"]["id"] for e in current["R-TRACE"]["links"] if e["type"] == "allocate"} == {"cube.function.manage-configuration"}
    assert {e["target"]["id"] for e in current["R-MODEL"]["links"] if e["type"] == "allocate"} == {"cube.function.measure-motion", "cube.function.evaluate-trace"}


def test_corner_detection_yaw_definition_and_printer_scope(review):
    _, _, changes = review
    current = {r["id"]: r for r in changes}
    assert current["R-DETECT"]["data"]["hardware_verification_required"] is True
    assert current["R-DETECT"]["data"]["acceptance_criteria"]["value"] == 8
    assert "Before starting balance control" in current["R-DETECT"]["data"]["statement"]
    assert {x["id"] for x in current["cube.verify.R-DETECT"]["data"]["unresolved_items"]} == {"R-DETECT.TBR.1"}
    assert current["R-YAW"]["data"]["coordinate_frame_ref"]["id"] == "cube.definition.balance-frame"
    assert "fixed" in current["cube.definition.balance-frame"]["data"]["yaw_rate"]
    for id in ["I-PRINT-X", "I-PRINT-Y", "I-PRINT-Z"]:
        assert current[id]["data"]["value"] == 256
        assert current[id]["data"]["origin"] == "manufacturer_specification"


def test_review_is_repeatable_keeps_numeric_contract_and_projects_constraint_nodes(review):
    module, history, changes = review
    assert canonical_bytes(module["build_review"](history + changes)) == canonical_bytes(changes)
    rows = {(r["id"], r["revision"]): r for r in history + changes}
    Store._check_references(rows.values())
    new = next(r for r in changes if r["kind"] == "simulation_snapshot")
    old = rows[new["id"], module["SOURCE"]]
    for field in ["model", "controller", "contract", "plan", "families"]:
        assert new["data"][field] == old["data"][field]
    cube = project_model(rows, next(r for r in changes if r["kind"] == "system_model"))["balancing_cube"]
    assert cube["counts"] == {"obligations": 19, "groups": 7, "verification_cases": 22, "linked_kdps": 37}
    assert len(cube["constraints"]) == 3
    assert len(cube["reviewed_architecture"]["functions"]) == 9
    assert all(r["record_role"] != "constraint" for r in cube["requirements"])
    assert next(p for p in cube["kdps"] if p["id"] == "D-BUDGET")["requirement_refs"][0]["id"] == "C-BUDGET"
    assert "C-FIT-MATERIAL" not in json.dumps(cube["groups"])


def test_later_model_ids_do_not_leak_into_a_historical_snapshot(review):
    module, history, changes = review
    old = next(r for r in history if r["id"] == "cube.simulation.snapshot" and r["revision"] == module["SOURCE"])
    selected = current_records(history + changes, snapshot=old)
    assert len([r for r in selected if r["kind"] == "function"]) == 8
    assert not {"R-DETECT", "O-HOLD-INTERVAL", "cube.definition.balance-frame", "cube.function.manage-configuration", "cube.verify.R-DETECT"} & {r["id"] for r in selected}
