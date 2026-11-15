"""Adapt existing Cube trajectories to the requirement-shortfall contract."""
from __future__ import annotations

import math

from .scoring import combined_status, evaluate_requirements, finite_number

METHOD = "requirement_max_deficit_v1"


def hold_measurements(record, *, duration_s, control_period_s):
    """Use the first hold interval, including release; interpolate its endpoint.

    RMS is time weighted. A truncated/gapped trajectory cannot establish a
    whole-interval pass, but observed peak violations remain useful failures.
    """
    summary, rows = record.get("summary", {}), record.get("rows", [])
    elapsed = summary.get("simulated_duration_s")
    values = {"unsupported_vertex_hold_duration": None}
    fields = ("time_s", "tilt_total_deg", "pivot_displacement_mm")
    if len(rows) < 2 or any(not finite_number(r.get(k)) for r in rows for k in fields):
        return values
    if rows[0]["time_s"] != 0 or any(b["time_s"] <= a["time_s"] for a, b in zip(rows, rows[1:])):
        return values
    if any(b["time_s"] - a["time_s"] > 3 * control_period_s + 1e-8 for a, b in zip(rows, rows[1:])):
        return values
    if finite_number(elapsed) and elapsed >= 0 and abs(elapsed - rows[-1]["time_s"]) <= 1e-8:
        values["unsupported_vertex_hold_duration"] = min(elapsed, duration_s)
    window = [r for r in rows if r["time_s"] <= duration_s]
    after = next((r for r in rows if r["time_s"] > duration_s), None)
    if window[-1]["time_s"] < duration_s and after:
        a = window[-1]
        ratio = (duration_s - a["time_s"]) / (after["time_s"] - a["time_s"])
        window.append({k: a[k] + ratio * (after[k] - a[k]) for k in fields})
    complete = (summary.get("status") == "completed" and finite_number(elapsed)
                and elapsed >= duration_s - 1e-8 and window[-1]["time_s"] >= duration_s - 1e-8
                and all(b["time_s"] - a["time_s"] <= 3 * control_period_s + 1e-8
                        for a, b in zip(window, window[1:])))
    if not complete and values["unsupported_vertex_hold_duration"] == duration_s:
        values["unsupported_vertex_hold_duration"] = None
    peak = max(r["tilt_total_deg"] for r in window)
    drift = max(r["pivot_displacement_mm"] for r in window)
    # Peaks on a partial interval may prove a violation, never a full pass.
    values.update(peak_tilt_deg=peak, peak_pivot_displacement_mm=drift)
    if complete:
        integral = sum((b["time_s"] - a["time_s"]) *
                       (a["tilt_total_deg"] ** 2 + b["tilt_total_deg"] ** 2) / 2
                       for a, b in zip(window, window[1:]))
        values["hold_interval_tilt_rms_deg"] = math.sqrt(integral / duration_s)
    values["interval_complete"] = complete
    return values


def evaluate_cube_records(records, snapshot):
    contract = snapshot["contract"]["requirement_scoring"]
    duration = snapshot["contract"]["screening"]["required_duration_s"]
    period = snapshot["model"]["physics"]["control_period_s"]
    hold = next(r for r in contract["rules"] if r["requirement_ref"]["id"] == "R-HOLD")
    if contract.get("method") != METHOD or duration != hold["limit"]:
        raise ValueError("Scoring method or hold interval disagrees with the requirement contract")
    cases = []
    for record in records:
        values = hold_measurements(record, duration_s=duration, control_period_s=period)
        if not values.get("interval_complete"):
            for rule in contract["rules"]:
                metric = rule["metric"]
                if rule["operator"] == "<=" and finite_number(values.get(metric)):
                    if values[metric] <= rule.get("limit", math.inf):
                        values[metric] = None
        evaluation = evaluate_requirements(contract, values, domain="simulation")
        cases.append({"case_ref": {k: record.get(k) for k in ("run_id", "domain_id", "condition_id", "seed")},
                      **evaluation})
    results = []
    for rule in contract["rules"]:
        entries = [next(r for r in c["requirement_results"] if r["requirement_ref"] == rule["requirement_ref"]) for c in cases]
        deficits = [r["deficit"] for r in entries if r["deficit"] is not None]
        results.append({**rule, "status": combined_status(entries),
                        "deficit": max(deficits) if entries and len(deficits) == len(entries) else None,
                        "max_known_deficit": max(deficits) if deficits else None})
    active = [r for r in results if r.get("simulation_proxy", False)]
    known = [r["deficit"] for r in active if r["deficit"] is not None]
    deficit = max(known) if active and len(known) == len(active) else None
    return {"contract_ref": contract["ref"], "evidence_domain": "simulation",
            "overall_status": combined_status(results), "search_status": combined_status(active),
            "max_deficit": deficit, "score": -deficit if deficit is not None else None,
            "max_known_deficit": max((r["max_known_deficit"] for r in active if r["max_known_deficit"] is not None), default=None),
            "physical_status": "unjudged", "requirement_results": results, "cases": cases,
            "unjudged_requirements": [r["requirement_ref"] for r in results if r["status"] == "unjudged"],
            "scope": "corner-000 numerical development; no eight-corner, repetition, electrical, thermal or hardware verification"}


def selection_key(result):
    """Rank only comparable contracts; a valid in-scope pass precedes a fail."""
    value = result.get("requirement_evaluation")
    if value is None:  # Legacy contracts retain their original ordering.
        return (0, result["score"])
    if value["score"] is None:
        return (-1, -math.inf)
    return (int(value["search_status"] == "pass"), value["score"])
