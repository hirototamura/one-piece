import copy
import json
from pathlib import Path
import runpy

import pytest

from onepiece.cube_scoring import evaluate_cube_records, hold_measurements, selection_key
from onepiece.model import canonical_bytes
from onepiece.scoring import assess, evaluate_requirements
from onepiece.store import Store

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def snapshot():
    load = runpy.run_path(str(ROOT / "projects/balancing-cube/refine_model.py"))["load_records"]
    module = runpy.run_path(str(ROOT / "projects/balancing-cube/adopt_requirement_scoring.py"))
    history = load(ROOT / "projects/balancing-cube/store")
    changes = module["build_contract"](history)
    assert canonical_bytes(changes) == canonical_bytes(module["build_contract"](history + changes))
    Store._check_references(history + changes)
    return next(r["data"] for r in changes if r["kind"] == "simulation_snapshot")


@pytest.mark.parametrize("value,op,limit,status,deficit", [
    (3, "<=", 2, "fail", .5), (.2, "<=", 2, "pass", 0),
    (8, ">=", 10, "fail", .2), (20, ">=", 10, "pass", 0),
    (False, "==", True, "fail", 1), (True, "==", True, "pass", 0),
    (None, "<=", 2, "unjudged", None), (float("nan"), "<=", 2, "unjudged", None),
    (True, "<=", 2, "unjudged", None), (1, "==", True, "unjudged", None),
    (10, "<=", None, "unjudged", None), (8, "==", 8, "pass", 0),
])
def test_shortfall(value, op, limit, status, deficit):
    actual, amount = assess(value, op, limit)
    assert actual == status
    assert amount is None if deficit is None else amount == pytest.approx(deficit)


def trial(tilt=1., drift=1., end=10.005, status="completed"):
    rows = [{"time_s": i * .015, "tilt_total_deg": tilt, "pivot_displacement_mm": drift}
            for i in range(round(end / .015) + 1)]
    return {"run_id": "case-1", "domain_id": "nominal", "condition_id": "release-a", "seed": 1,
            "summary": {"status": status, "simulated_duration_s": rows[-1]["time_s"]}, "rows": rows}


def test_contract_preserves_existing_physics_and_only_proxies_four_requirements(snapshot):
    store = Store(ROOT / "projects/balancing-cube/store")
    source = next(r["data"] for r in store.records("balancing-cube") if r["id"] == "cube.simulation.snapshot" and r["revision"] == "bottom-corner-000-20261017-3")
    for field in ("model", "controller", "parameter_bindings", "families"):
        assert snapshot[field] == source[field]
    assert snapshot["plan"]["exploration"] == source["plan"]["exploration"]
    assert snapshot["plan"]["validation"] == source["plan"]["validation"]
    rules = snapshot["contract"]["requirement_scoring"]["rules"]
    assert len(rules) == 22
    assert {r["requirement_ref"]["id"] for r in rules if r["simulation_proxy"]} == {"R-HOLD", "R-TILT", "R-RMS", "R-DRIFT"}
    assert next(r for r in rules if r["requirement_ref"]["id"] == "R-YAW")["limit"] is True


def test_sufficient_performance_ties_and_one_violation_disqualifies(snapshot):
    a = evaluate_cube_records([trial()], snapshot)
    b = evaluate_cube_records([trial(.01, .01)], snapshot)
    assert a["score"] == b["score"] == 0
    assert a["search_status"] == "pass"
    assert a["overall_status"] == a["physical_status"] == "unjudged"
    bad = evaluate_cube_records([trial(.01, .01), trial(3)], snapshot)
    assert bad["search_status"] == bad["overall_status"] == "fail"
    assert bad["max_deficit"] == pytest.approx(.5)
    assert selection_key({"requirement_evaluation": a}) > selection_key({"requirement_evaluation": bad})
    assert evaluate_cube_records([trial(6)], snapshot)["max_deficit"] == pytest.approx(2)


def test_whole_interval_not_final_second_and_no_truncated_pass(snapshot):
    record = trial()
    for row in record["rows"]:
        row["tilt_total_deg"] = 4 if row["time_s"] < 9 else .01
    measured = hold_measurements(record, duration_s=10, control_period_s=.015)
    assert measured["hold_interval_tilt_rms_deg"] > 3
    failed = evaluate_cube_records([record], snapshot)
    assert failed["search_status"] == "fail"
    early = evaluate_cube_records([trial(end=6, status="lost_balance")], snapshot)
    assert early["search_status"] == "fail"
    hold = next(r for r in early["requirement_results"] if r["requirement_ref"]["id"] == "R-HOLD")
    assert hold["deficit"] == pytest.approx(.4)
    assert early["max_deficit"] is None  # RMS for the missing interval is unknown.
    assert early["max_known_deficit"] == pytest.approx(.4)


def test_missing_gapped_and_nonfinite_evidence_never_passes(snapshot):
    for kind in ("missing", "gap", "nan"):
        record = trial()
        if kind == "missing":
            record["rows"] = []
        elif kind == "gap":
            del record["rows"][1:100]
        else:
            record["rows"][5]["tilt_total_deg"] = float("nan")
        result = evaluate_cube_records([record], snapshot)
        assert result["search_status"] == "unjudged"
        assert result["score"] is None
        json.dumps(result, allow_nan=False)


def test_unresolved_limits_and_kdp_changes_do_not_invent_rewards(snapshot):
    contract = snapshot["contract"]["requirement_scoring"]
    values = {r["metric"]: r["limit"] for r in contract["rules"]}
    hardware = evaluate_requirements(contract, values, domain="hardware")
    assert hardware["physical_status"] == "unjudged"
    changed = copy.deepcopy(snapshot)
    changed["kdps"]["entries"][0]["value"] = 1e10
    assert evaluate_cube_records([trial()], changed) == evaluate_cube_records([trial()], snapshot)


def test_repeatability_needs_the_declared_sample_count_and_mandatory_failure_wins(snapshot):
    contract = snapshot["contract"]["requirement_scoring"]
    result = evaluate_requirements(contract, {"successful_hold_trials": 9}, domain="hardware")
    repeat = next(r for r in result["requirement_results"] if r["requirement_ref"]["id"] == "R-REPEAT")
    assert repeat["status"] == "unjudged"
    result = evaluate_requirements(contract, {"successful_hold_trials": 8, "successful_hold_trials_sample_count": 10}, domain="hardware")
    assert result["overall_status"] == "fail"
    repeat = next(r for r in result["requirement_results"] if r["requirement_ref"]["id"] == "R-REPEAT")
    assert repeat["deficit"] == pytest.approx(1 / 9)


def test_scoring_and_constraints_are_pinned_in_agent_context(snapshot):
    store = Store(ROOT / "projects/balancing-cube/store")
    context = store.context("balancing-cube", kinds=["design"], max_designs=0, max_evidence=0,
                            snapshot_ref={"id": "cube.simulation.snapshot", "revision": "requirement-scoring-20261115-2"})
    contracts = [r for r in context["records"] if r["kind"] == "evaluation_contract"]
    assert len(contracts) == 1
    assert contracts[0]["revision"] == "requirement-scoring-20261115-2"
    assert len([r for r in context["records"] if r["kind"] == "constraint"]) == 3
