"""Heuristic design agent for the thermal-loop autonomous trade."""

from __future__ import annotations

from typing import Any


def _target_metric(targets: list[dict[str, Any]], key: str, default: float) -> float:
    for item in targets:
        if item.get("key") == key and item.get("targetValue") is not None:
            return float(item["targetValue"])
    return default


def propose_parameter_updates(
    parameters: dict[str, float],
    metrics: dict[str, float],
    goal_targets: list[dict[str, Any]],
) -> tuple[dict[str, float], list[dict[str, str]]]:
    """Return updated parameter values plus mutation records."""
    target_mass = _target_metric(goal_targets, "radiatorMassKg", 15.7)
    min_efficiency = _target_metric(goal_targets, "rejectionEfficiency", 0.94)
    min_margin = _target_metric(goal_targets, "heatBalanceMarginKw", 0.0)

    current_area = float(parameters["P-RAD-AREA"])
    current_mass = float(parameters["P-RAD-MASS"])
    current_flow = float(parameters["P-COOLANT-FLOW"])
    current_efficiency = float(metrics.get("rejectionEfficiency", min_efficiency))
    current_margin = float(metrics.get("heatBalanceMarginKw", 0.0))

    next_area = current_area
    next_mass = current_mass
    next_flow = current_flow

    if current_efficiency > min_efficiency + 0.02 and current_margin > min_margin + 0.2:
      next_area = max(5.4, round(current_area - 0.22, 3))
      next_mass = max(target_mass, round(current_mass - 0.62, 3))
      next_flow = round(current_flow + 0.03, 3)
    elif current_margin < min_margin or current_efficiency < min_efficiency:
      next_area = round(current_area + 0.11, 3)
      next_mass = round(current_mass + 0.08, 3)
      next_flow = round(current_flow + 0.05, 3)
    elif current_mass > target_mass:
      next_area = max(5.5, round(current_area - 0.15, 3))
      next_mass = max(target_mass, round(current_mass - 0.45, 3))
      next_flow = round(current_flow + 0.04, 3)

    next_values = {
        "P-RAD-AREA": next_area,
        "P-RAD-MASS": next_mass,
        "P-COOLANT-FLOW": next_flow,
        "P-HEAT-LOAD": float(parameters["P-HEAT-LOAD"]),
    }

    mutations: list[dict[str, str]] = []
    for key, field, node_id in (
        ("P-RAD-AREA", "value", "param-rad-area"),
        ("P-RAD-MASS", "value", "param-rad-mass"),
        ("P-COOLANT-FLOW", "value", "param-coolant-flow"),
    ):
        previous = float(parameters[key])
        new_value = float(next_values[key])
        if abs(previous - new_value) < 1e-9:
            continue
        mutations.append(
            {
                "nodeKind": "design_parameter",
                "nodeId": node_id,
                "nodeKey": key,
                "fieldPath": field,
                "previousValue": f"{previous}",
                "newValue": f"{new_value}",
                "criticalityTier": "derived",
                "rationale": "Design agent trade step.",
            }
        )

    return next_values, mutations
