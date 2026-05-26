#!/usr/bin/env python3
"""Propulsion thrust margin check — SSOT-bound design script (logic automation)."""

# SSOT:PARAM:P-VBUS = 400
# SSOT:PARAM:P-M-MOTOR = 12.4

VBUS = 400
MOTOR_MASS_KG = 12.4
MTOW_KG = 820
GRAVITY = 9.81
REQUIRED_TWR = 1.15


def main() -> None:
    thrust_required_n = MTOW_KG * GRAVITY * REQUIRED_TWR
    power_nominal_kw = VBUS * 180 / 1000  # illustrative bus current
    print(
        f"Thrust margin check: required {thrust_required_n:.0f} N "
        f"at MTOW {MTOW_KG} kg (T/W≥{REQUIRED_TWR}); "
        f"motor mass {MOTOR_MASS_KG} kg; nominal bus {VBUS} V, ~{power_nominal_kw:.1f} kW"
    )


if __name__ == "__main__":
    main()
