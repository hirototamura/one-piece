"""Append the human-approved requirement shortfall contract and executable child."""
from __future__ import annotations

import copy
from pathlib import Path
import runpy

from onepiece.model import digest, make_record, ref
from onepiece.store import Store

ROOT = Path(__file__).resolve().parent
REVISION = "requirement-scoring-20261115-2"
REQUIREMENTS = "requirements-review-20261115-3"
EXECUTABLE = "bottom-corner-000-20261017-3"
CONTRACT_ID = "cube.evaluation.requirement-shortfall"
PROXIES = {"R-HOLD": "unsupported_vertex_hold_duration", "R-TILT": "peak_tilt_deg",
           "R-RMS": "hold_interval_tilt_rms_deg", "R-DRIFT": "peak_pivot_displacement_mm"}


def build_contract(history):
    by = {(r["id"], r["revision"]): r for r in history}
    source = by["cube.simulation.snapshot", REQUIREMENTS]
    executable = by["cube.simulation.snapshot", EXECUTABLE]
    ctx = source["data"]["context_refs"]
    requirements = [by[r["id"], r["revision"]] for category in ("requirements", "constraints") for r in ctx[category]]
    parameters = [by[r["id"], r["revision"]] for r in ctx["kdps"]]
    rules = []
    for r in requirements:
        d = r["data"]
        if d.get("record_role") == "requirement_group":
            continue
        acceptance = d["acceptance_criteria"]
        limit = acceptance.get("value")
        if r["id"] == "C-JAPAN":
            limit = True  # One Boolean attestation covering all purchased parts.
        related = [p for p in parameters if ref(r) in p["data"].get("requirement_refs", [])]
        rules.append({"requirement_ref": ref(r), "mandatory": True,
                      "record_role": d["record_role"], "metric": PROXIES.get(r["id"], acceptance["metric"]),
                      "operator": acceptance["operator"], "limit": limit, "unit": acceptance.get("unit"),
                      "sample_count": acceptance.get("sample_count"),
                      "limit_resolved": acceptance.get("limits_status") != "unresolved" and limit is not None,
                      "simulation_proxy": r["id"] in PROXIES,
                      "kdp_refs": [ref(p) for p in related],
                      "kdp_origins": [{"ref": ref(p), "origin": p["data"].get("origin")} for p in related]})

    def add(id, kind, data, links=()):
        return make_record(project_id="balancing-cube", id=id, revision=REVISION, kind=kind,
                           created_at="2026-11-15T14:36:00+00:00", product_node="cube.verification",
                           actor={"type": "human", "id": "hirototamura"}, data=data, links=list(links))
    contract = add(CONTRACT_ID, "evaluation_contract", {
        "ref": ref(CONTRACT_ID, REVISION), "method": "requirement_max_deficit_v1",
        "approval_state": "human_reviewed", "authorization": "User accepted mandatory per-requirement gates, normalized shortfalls, D=max(d), no KDP rewards, separate numerical/physical evidence, and requested implementation.",
        "source_requirements_snapshot_ref": ref(source), "rules": rules,
        "formula": "upper: max(0,x/L-1); lower: max(0,1-x/L); D=max(d); score=-D",
        "selection": "in-scope pass before fail; minimize D; unknown D is not rankable; equal deficits tie",
        "unknown_policy": "No fabricated value, pass, physical confidence or reward for unmeasured quantities.",
        "aggregation": "worst measured shortfall across cases, then across independent requirements; no sum or average",
        "repeat_scope": "R-REPEAT requires an explicit ten-trial hardware protocol; existing 12 numerical development cases do not constitute it.",
    })
    if (CONTRACT_ID, "requirement-scoring-20261115-1") in by:
        contract["data"]["supersedes"] = ref(CONTRACT_ID, "requirement-scoring-20261115-1")
    s = copy.deepcopy(executable["data"])
    s.update(supersedes=ref(executable), source_snapshot_ref=ref(executable),
             requirements_snapshot_ref=ref(source), scoring_contract_ref=ref(contract),
             operating_parameters=copy.deepcopy(source["data"]["operating_parameters"]),
             reference_frames=copy.deepcopy(source["data"]["reference_frames"]),
             history_only=False, trial_scope="corner-000 numerical development under the ten-second shortfall contract")
    # Keep the executable physics, controller, parameter bindings and baseline
    # provenance. Only the reviewed requirement/KDP context and evaluator change.
    for category in ("requirements", "constraints", "kdps", "functions", "products", "verification_cases", "operating_parameters", "definitions"):
        s["context_refs"][category] = copy.deepcopy(ctx[category])
    s["context_refs"]["scoring_contract"] = ref(contract)
    s["kdps"] = copy.deepcopy(source["data"]["kdps"])
    s["mission"] = copy.deepcopy(source["data"]["mission"])
    s["contract"]["requirement_scoring"] = copy.deepcopy(contract["data"])
    s["contract"]["revision"] = REVISION
    s["contract"]["screening"].update(required_duration_s=10., criteria=[
        {"requirement_ref": r["requirement_ref"], "metric": r["metric"], "operator": r["operator"], "limit": r["limit"], "unit": r["unit"]}
        for r in rules if r["simulation_proxy"]], threshold_status="requirement_proxies_not_hardware_acceptance")
    s["plan"]["objective"] = {"method": "requirement_max_deficit_v1", "contract_ref": ref(contract),
                              "formula": "score=-max_deficit; pass before fail; no reward beyond requirements"}
    s["plan"]["revision"] = REVISION
    # Preserve CPU/GPU numerical qualification independently of new pass metrics.
    s["contract"]["cpu_gpu_agreement"]["near_gate_margins"] = {}
    snapshot = add("cube.simulation.snapshot", "simulation_snapshot", s,
                   [{"type": "derive", "target": ref(executable)}, {"type": "derive", "target": ref(source)}])
    baseline = add("cube.baseline.requirement-scoring", "baseline", {
        "reason": "User-approved requirement scoring implementation; no hardware adoption or rescoring of historical runs.",
        "members": [{**ref(r), "sha256": digest(r)} for r in (contract, snapshot)],
        "physical_verified": False, "adopted_design_baseline": False})
    return [contract, snapshot, baseline]


if __name__ == "__main__":
    load = runpy.run_path(str(ROOT / "refine_model.py"))["load_records"]
    print(Store(ROOT / "store").import_records(build_contract(load(ROOT / "store"))))
