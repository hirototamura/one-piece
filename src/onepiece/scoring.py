"""Requirement conformance and capped, dimensionless shortfalls; no KDP rewards."""
from __future__ import annotations

import math


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def assess(value, operator, limit):
    """Return (status, deficit). Missing values/limits never establish a pass."""
    if value is None or limit is None:
        return "unjudged", None
    if operator in {"<=", ">="}:
        if not finite_number(value) or not finite_number(limit) or limit <= 0:
            return "unjudged", None
        deficit = max(0., value / limit - 1 if operator == "<=" else 1 - value / limit)
        return ("pass" if deficit == 0 else "fail"), deficit
    if operator != "==":
        raise ValueError("Unsupported requirement operator")
    if isinstance(limit, bool):
        if not isinstance(value, bool):
            return "unjudged", None
        return ("pass", 0.) if value is limit else ("fail", 1.)
    if finite_number(limit):
        if not finite_number(value):
            return "unjudged", None
        passed = value == limit
        deficit = abs(value - limit) / abs(limit) if limit else float(not passed)
        return ("pass" if passed else "fail"), deficit
    if not isinstance(value, type(limit)):
        return "unjudged", None
    return ("pass", 0.) if value == limit else ("fail", 1.)


def combined_status(results):
    statuses = [r["status"] for r in results if r.get("mandatory", True)]
    if "fail" in statuses:
        return "fail"
    return "pass" if statuses and all(s == "pass" for s in statuses) else "unjudged"


def evaluate_requirements(contract, measurements, *, domain):
    """Evaluate exactly the declared rules; input is evidence, never KDP values.

    The caller declares its evidence domain. Simulation cannot establish hardware
    conformance. Unresolved source limits remain unknown even if data is supplied.
    """
    if domain not in {"simulation", "hardware"}:
        raise ValueError("Unknown evidence domain")
    results = []
    seen = set()
    for rule in contract["rules"]:
        reference = rule["requirement_ref"]
        key = reference["id"], reference["revision"]
        if key in seen:
            raise ValueError("Duplicate requirement rule")
        seen.add(key)
        value = measurements.get(rule["metric"])
        available = domain == "hardware" or rule.get("simulation_proxy", False)
        if rule.get("sample_count") is not None and measurements.get(rule["metric"] + "_sample_count") != rule["sample_count"]:
            available = False
        limit = rule.get("limit") if rule.get("limit_resolved", True) else None
        status, deficit = assess(value, rule["operator"], limit) if available else ("unjudged", None)
        results.append({**rule, "value": value if available and not (isinstance(value, float) and not math.isfinite(value)) else None,
                        "status": status, "deficit": deficit, "evidence_domain": domain})
    active = [r for r in results if domain == "hardware" or r.get("simulation_proxy", False)]
    complete = bool(active) and all(r["deficit"] is not None for r in active)
    known = [r["deficit"] for r in active if r["deficit"] is not None]
    deficit = max(known) if complete else None
    return {"contract_ref": contract["ref"], "evidence_domain": domain,
            "requirement_results": results, "overall_status": combined_status(results),
            "search_status": combined_status(active), "max_deficit": deficit,
            "max_known_deficit": max(known) if known else None,
            "score": -deficit if deficit is not None else None,
            "physical_status": combined_status(results) if domain == "hardware" else "unjudged",
            "interpretation": "score = -max_deficit within the declared scope; not a pass rate or success probability"}
