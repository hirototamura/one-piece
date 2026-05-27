#!/usr/bin/env python3
"""Thermal rejection stand-in for autonomous co-design loops."""

from __future__ import annotations

import json

# SSOT:PARAM:P-RAD-AREA = 6.8
# SSOT:PARAM:P-RAD-MASS = 18.5
# SSOT:PARAM:P-HEAT-LOAD = 15.2
# SSOT:PARAM:P-COOLANT-FLOW = 0.72

RADIATOR_AREA_M2 = 6.8
RADIATOR_MASS_KG = 18.5
HEAT_LOAD_KW = 15.2
COOLANT_FLOW_KGPS = 0.72

BASELINE_EFFICIENCY = 0.94


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(value, hi))


def main() -> None:
    rejected_kw = (RADIATOR_AREA_M2 * 2.25) + (COOLANT_FLOW_KGPS * 2.4)
    efficiency = clamp(rejected_kw / HEAT_LOAD_KW, 0.0, 0.99)
    heat_balance_margin_kw = rejected_kw - HEAT_LOAD_KW
    goal_delta = efficiency - BASELINE_EFFICIENCY

    print(
        "Thermal rejection check: "
        f"area {RADIATOR_AREA_M2:.2f} m2, mass {RADIATOR_MASS_KG:.2f} kg, "
        f"efficiency {efficiency:.3f}, margin {heat_balance_margin_kw:.2f} kW",
    )
    print(
        "METRICS:"
        + json.dumps(
            {
                "radiatorMassKg": round(RADIATOR_MASS_KG, 3),
                "rejectionEfficiency": round(efficiency, 3),
                "heatBalanceMarginKw": round(heat_balance_margin_kw, 3),
                "efficiencyDeltaVsBaseline": round(goal_delta, 3),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
