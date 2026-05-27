"""Requirements-side evaluation for autonomous co-design."""

from __future__ import annotations

from typing import Any


def _target_metric(targets: list[dict[str, Any]], key: str, default: float) -> float:
    for item in targets:
        if item.get("key") == key and item.get("targetValue") is not None:
            return float(item["targetValue"])
    return default


def evaluate_requirements(
    metrics: dict[str, float],
    goal_targets: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], bool, str]:
    """Return requirement-style checks, convergence flag, and summary text."""
    target_mass = _target_metric(goal_targets, "radiatorMassKg", 15.7)
    min_efficiency = _target_metric(goal_targets, "rejectionEfficiency", 0.94)
    min_margin = _target_metric(goal_targets, "heatBalanceMarginKw", 0.0)

    mass = float(metrics.get("radiatorMassKg", 0.0))
    efficiency = float(metrics.get("rejectionEfficiency", 0.0))
    margin = float(metrics.get("heatBalanceMarginKw", -999.0))

    checks = [
        {
            "requirementId": "req-s3",
            "requirementKey": "SR-030",
            "status": "pass" if margin >= min_margin else "fail",
            "note": (
                f"Heat balance margin {margin:.3f} kW vs target ≥ {min_margin:.3f} kW."
            ),
        },
        {
            "requirementId": "req-sub4",
            "requirementKey": "TR-200",
            "status": "pass" if efficiency >= min_efficiency else "fail",
            "note": (
                f"Rejection efficiency {efficiency:.3f} vs target ≥ {min_efficiency:.3f}."
            ),
        },
        {
            "requirementId": "dc-2",
            "requirementKey": "DC-TH-004",
            "status": "pass" if mass <= target_mass else "improving",
            "note": f"Radiator mass {mass:.3f} kg vs target ≤ {target_mass:.3f} kg.",
        },
    ]

    converged = mass <= target_mass and efficiency >= min_efficiency and margin >= min_margin
    summary = (
        "Converged: all thermal checks green."
        if converged
        else "Requirements agent requests another design/simulation iteration."
    )
    return checks, converged, summary
