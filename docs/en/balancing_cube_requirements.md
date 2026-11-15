# Balancing Cube requirements and constraints

`requirements-review-20261115-3` · 2026-11-15

19 requirements, 7 classification groups, 3 separate constraints. Checks remain planned/not run.

`O-HOLD-INTERVAL = 10 s` · [Review / 改訂の根拠](cube_requirements_review.md)

Regenerate: `python projects/balancing-cube/apply_requirement_review.py --write-docs`.

## C-BUDGET: First prototype cost

`C-BUDGET@requirements-review-20261115-3` · constraint · project · not_run

The cost of the first Cube prototype shall be no more than the approved budget.

Acceptance / 合否基準: {"limit_ref": {"id": "D-BUDGET", "revision": "requirements-review-20261115-3"}, "metric": "prototype_cost", "operator": "<=", "unit": "JPY"}

The prototype needs an explicit cost limit.

Verification method: analysis

Open items / 未解決事項:
- C-BUDGET.TBR.1: Set the budget and cost scope. D-BUDGET has no value.

## C-FIT: Manufacturing and installation requirement set

`C-FIT@requirements-review-20261115-3` · requirement_group · subsystem · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

This node groups requirements. It is not a separate test obligation.

Derived from: cube.req.mechanical

## C-FIT-INSTALL: Installed component dimensions

`C-FIT-INSTALL@requirements-review-20261115-3` · requirement · subsystem · not_run

Each installed component shall have dimensions no more than the specified dimensions of its space in the Cube housing.

Acceptance / 合否基準: {"limits_status": "unresolved", "metric": "installed_components_inside_assigned_space", "operator": "==", "unit": "1", "value": true}

This obligation is one part of the original compound manufacturing requirement.

Derived from: C-FIT

Allocation: cube.component.frame-housing, cube.component.reaction-wheels, cube.component.motor-drivers, cube.component.imu, cube.component.controller, cube.component.power-bus

Verification method: inspection

Open items / 未解決事項:
- C-FIT-INSTALL.TBR.1: Identify printer limits, the material list, component dimensions and required movement clearance.

## C-FIT-PRINT: Printed part dimensions

`C-FIT-PRINT@requirements-review-20261115-3` · constraint · manufacturing · not_run

Each printed housing part shall have dimensions no more than the specified build limits of the 3D printer.

Acceptance / 合否基準: {"metric": "printed_parts_inside_build_volume", "operator": "==", "unit": "1", "value": true}

Conditions / 条件:
- Check each printed part in its planned print orientation against the printer build volume; do not limit the assembled Cube envelope.

This obligation is one part of the original compound manufacturing requirement.

Verification method: inspection

Open items / 未解決事項:
- C-FIT-PRINT.TBR.1: Check actual part geometry, print orientation and process clearance on Bambu Lab A1.

## C-JAPAN: Component supply to Japan

`C-JAPAN@requirements-review-20261115-3` · constraint · manufacturing · not_run

The Cube shall use components that suppliers can supply to Japan.

Acceptance / 合否基準: {"metric": "components_available_for_supply_to_japan", "operator": "==", "unit": "1", "value": "all_purchased_components"}

The user needs to obtain parts in Japan.

Verification method: inspection

Open items / 未解決事項:
- C-JAPAN.TBR.1: Define acceptable lead time and supply cost. The source word 'easy' has no numerical limit.

## C-PRINT: Housing manufacture

`C-PRINT@requirements-review-20261115-3` · requirement · subsystem · not_run

The Cube housing shall be a part that the specified 3D printer can make.

Acceptance / 合否基準: {"metric": "housing_manufacturable", "operator": "==", "requirement_ref": {"id": "C-FIT-PRINT", "revision": "requirements-review-20261115-3"}, "unit": "1", "value": true}

The user intends to use a friend's 3D printer.

Derived from: cube.req.mechanical

Allocation: cube.component.frame-housing

Verification method: demonstration

Open items / 未解決事項:
- C-PRINT.TBR.1: Confirm the print recipe and demonstrate manufacture on the specified Bambu Lab A1. Material remains a design choice.

## M-VERTEX: Vertex hold mission

`M-VERTEX@requirements-review-20261115-3` · requirement · mission · not_run

The Cube shall balance on each of its 8 corners with its 3 reaction wheels.

Acceptance / 合否基準: {"domain": "hardware", "metric": "distinct_corners_demonstrated", "operator": "==", "unit": "count", "value": 8}

This mission requires a physical demonstration of the Cube concept.

Allocation: cube.system

Verification method: test

Open items / 未解決事項:
- M-VERTEX.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

## R-DETECT: Support-corner identification

`R-DETECT@requirements-review-20261115-3` · requirement · subsystem · not_run

Before starting balance control, the control system shall automatically identify the target support corner from the Cube's 8 corners.

Acceptance / 合否基準: {"metric": "correctly_identified_support_corners", "operator": "==", "value": 8, "unit": "count", "domain": "hardware"}

Conditions / 条件:
- Identify the support corner using attitude/sensor information before enabling balance control.

The eight-corner mission requires the appropriate support-corner frame before balance control starts.

Derived from: M-VERTEX

Allocation: cube.function.estimate-attitude

Verification method: test

Open items / 未解決事項:
- R-DETECT.TBR.1: Define the valid initial attitude/sensor conditions and handling of an ambiguous corner. No new numeric tolerance is assumed.

## R-DRIFT: Contact point movement

`R-DRIFT@requirements-review-20261115-3` · requirement · system · not_run

During the hold interval, the Cube contact point shall move no more than 2 mm from its initial position.

Acceptance / 合否基準: {"domain": "hardware", "metric": "peak_contact_point_displacement", "operator": "<=", "unit": "mm", "value": 2}

Conditions / 条件:
- Use the first 10 s after manual release, as defined by O-HOLD-INTERVAL, as the hold interval.

This limit describes the Cube performance during the hardware hold test.

Derived from: M-VERTEX

Allocation: cube.function.control-balance, cube.function.maintain-contact

Verification method: test

Open items / 未解決事項:
- R-DRIFT.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

## R-DRIVE: Drive limit requirement set

`R-DRIVE@requirements-review-20261115-3` · requirement_group · subsystem · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

This node groups requirements. It is not a separate test obligation.

Derived from: cube.req.system

## R-DRIVE-CURRENT: Bus current limits

`R-DRIVE-CURRENT@requirements-review-20261115-3` · requirement · subsystem · not_run

The drive system shall keep the bus current between the approved minimum and maximum limits of the bus circuit.

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "bus_current_limit_exceeded", "operator": "==", "unit": "1", "value": false}

This obligation is one part of the original compound drive requirement.

Derived from: R-TILT, R-RMS

Allocation: cube.function.manage-power

Verification method: test

Open items / 未解決事項:
- R-DRIVE-CURRENT.TBR.1: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.
- R-DRIVE-CURRENT.TBR.2: Define the bus circuit ratings. Bus current does not show each motor winding current.

## R-DRIVE-SPEED: Wheel speed limits

`R-DRIVE-SPEED@requirements-review-20261115-3` · requirement · subsystem · not_run

Each reaction wheel shall have a speed magnitude no more than the approved limit for its assembly.

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "wheel_speed_limit_exceeded", "operator": "==", "unit": "1", "value": false}

This obligation is one part of the original compound drive requirement.

Derived from: R-TILT, R-RMS

Allocation: cube.function.generate-torque

Verification method: test

Open items / 未解決事項:
- R-DRIVE-SPEED.TBR.1: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

## R-DRIVE-TEMP: Component temperature limits

`R-DRIVE-TEMP@requirements-review-20261115-3` · requirement · subsystem · not_run

Each motor and driver shall have a temperature between its approved minimum and maximum limits.

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "component_temperature_limit_exceeded", "operator": "==", "unit": "1", "value": false}

This obligation is one part of the original compound drive requirement.

Derived from: R-TILT, R-RMS

Allocation: cube.function.manage-power

Verification method: test

Open items / 未解決事項:
- R-DRIVE-TEMP.TBR.1: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

## R-DRIVE-TORQUE: Motor torque limits

`R-DRIVE-TORQUE@requirements-review-20261115-3` · requirement · subsystem · not_run

At each measured speed, each motor shall have torque between its approved minimum and maximum limits.

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "motor_torque_envelope_exceeded", "operator": "==", "unit": "1", "value": false}

This obligation is one part of the original compound drive requirement.

Derived from: R-TILT, R-RMS

Allocation: cube.function.generate-torque

Verification method: test

Open items / 未解決事項:
- R-DRIVE-TORQUE.TBR.1: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

## R-DRIVE-VOLTAGE: Bus voltage limits

`R-DRIVE-VOLTAGE@requirements-review-20261115-3` · requirement · subsystem · not_run

The drive system shall keep the bus voltage between the approved minimum and maximum limits of each connected component.

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "bus_voltage_limit_exceeded", "operator": "==", "unit": "1", "value": false}

This obligation is one part of the original compound drive requirement.

Derived from: R-TILT, R-RMS

Allocation: cube.function.manage-power

Verification method: test

Open items / 未解決事項:
- R-DRIVE-VOLTAGE.TBR.1: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

## R-HOLD: Hold after manual release

`R-HOLD@requirements-review-20261115-3` · requirement · operational · not_run

After manual placement and release, the Cube shall hold its vertex position for at least 10 s without external support.

Acceptance / 合否基準: {"domain": "hardware", "metric": "unsupported_vertex_hold_duration", "operator": ">=", "unit": "s", "value": 10, "limit_ref": {"id": "O-HOLD-INTERVAL", "revision": "requirements-review-20261115-3"}}

Conditions / 条件:
- Use the first 10 s after manual release, as defined by O-HOLD-INTERVAL, as the hold interval.

The first prototype starts from manual placement. Automatic stand-up is outside this draft scope.

Derived from: M-VERTEX

Allocation: cube.function.control-balance, cube.function.maintain-contact

Verification method: test

Open items / 未解決事項:
- R-HOLD.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

## R-MODEL: Independent model comparison

`R-MODEL@requirements-review-20261115-3` · requirement · verification_platform · not_run

The verification platform shall compare model results with independent physical measurements under the same test conditions.

Acceptance / 合否基準: {"domain": "hardware_model_comparison", "metric": "model_error", "operator": "<=", "unit": "defined_per_quantity", "value": null}

CPU and GPU agreement checks numerical behavior. Physical measurements are necessary to assess model error.

Derived from: R-TILT, R-RMS

Allocation: cube.function.measure-motion, cube.function.evaluate-trace

Verification method: analysis

Open items / 未解決事項:
- R-MODEL.TBR.1: Define comparison quantities, units, error limits and independent physical data before a pass decision.

## R-REPEAT: Repeated hold tests

`R-REPEAT@requirements-review-20261115-3` · requirement · operational · not_run

Under fixed test conditions, the Cube shall pass the hold test in at least 9 of 10 trials.

Acceptance / 合否基準: {"domain": "hardware", "metric": "successful_hold_trials", "operator": ">=", "sample_count": 10, "unit": "trials/10", "value": 9}

Conditions / 条件:
- Use the first 10 s after manual release, as defined by O-HOLD-INTERVAL, as the hold interval.

Repeated trials check repeatability for the stated test conditions.

Derived from: R-HOLD

Allocation: cube.function.control-balance, cube.function.evaluate-trace

Verification method: test

Open items / 未解決事項:
- R-REPEAT.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.
- R-REPEAT.TBR.2: Define trial order, resets and the complete hold-test pass rule before testing.

## R-RMS: Tilt angle RMS

`R-RMS@requirements-review-20261115-3` · requirement · system · not_run

During the hold interval, the Cube shall have a tilt angle RMS no more than 2 deg.

Acceptance / 合否基準: {"domain": "hardware", "metric": "tilt_angle_rms", "operator": "<=", "unit": "deg", "value": 2}

Conditions / 条件:
- Use the first 10 s after manual release, as defined by O-HOLD-INTERVAL, as the hold interval.

This limit describes the Cube performance during the hardware hold test.

Derived from: M-VERTEX

Allocation: cube.function.control-balance

Verification method: test

Open items / 未解決事項:
- R-RMS.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

## R-SYNC: Video and MCU time relation

`R-SYNC@requirements-review-20261115-3` · requirement · verification_platform · not_run

The verification platform shall calculate the time relation between video and MCU timestamps with a time uncertainty no more than 0.005 s.

Acceptance / 合否基準: {"domain": "hardware", "metric": "video_mcu_time_uncertainty", "operator": "<=", "unit": "s", "value": 0.005}

A known time relation is necessary to compare independent measurements and controller logs.

Derived from: R-TILT, R-RMS

Allocation: cube.function.capture-synchronize

Verification method: test

Open items / 未解決事項:
- R-SYNC.TBR.1: Define the time uncertainty and calibration method. A 60 frame/s video alone does not demonstrate 0.005 s.

## R-TILT: Maximum tilt angle

`R-TILT@requirements-review-20261115-3` · requirement · system · not_run

During the hold interval, the Cube shall keep its tilt angle no more than 5 deg.

Acceptance / 合否基準: {"domain": "hardware", "metric": "peak_tilt_angle", "operator": "<=", "unit": "deg", "value": 5}

Conditions / 条件:
- Use the first 10 s after manual release, as defined by O-HOLD-INTERVAL, as the hold interval.

This limit describes the Cube performance during the hardware hold test.

Derived from: M-VERTEX

Allocation: cube.function.control-balance, cube.function.maintain-contact

Verification method: test

Open items / 未解決事項:
- R-TILT.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

## R-TRACE: Exact run references

`R-TRACE@requirements-review-20261115-3` · requirement · verification_platform · not_run

The verification platform shall identify the exact revisions of requirements, KDPs, designs, conditions, and results for each run.

Acceptance / 合否基準: {"metric": "missing_or_ambiguous_revision_references", "operator": "==", "unit": "count", "value": 0}

Exact references make changes and evidence applicability visible.

Derived from: R-MODEL, R-REPEAT

Allocation: cube.function.manage-configuration

Verification method: inspection

## R-VISION: Independent attitude measurement

`R-VISION@requirements-review-20261115-3` · requirement · verification_platform · not_run

The independent attitude measurement system shall have an angular standard uncertainty of no more than 0.5 deg.

Acceptance / 合否基準: {"domain": "hardware", "metric": "attitude_standard_uncertainty", "operator": "<=", "unit": "deg", "value": 0.5}

An independent measurement checks the attitude estimate used by the Cube.

Derived from: R-TILT, R-RMS

Allocation: cube.function.measure-motion

Verification method: test

Open items / 未解決事項:
- R-VISION.TBR.1: Define the attitude components, calibration method and uncertainty calculation. This draft uses standard uncertainty.

## R-YAW: Yaw rate monitoring

`R-YAW@requirements-review-20261115-3` · requirement · subsystem · not_run

During the hold interval, the control system shall monitor the yaw rate RMS.

Acceptance / 合否基準: {"metric": "yaw_rate_rms_recorded", "operator": "==", "target_only": {"unit": "deg/s", "value": 5}, "unit": "1", "value": true}

Conditions / 条件:
- Use the first 10 s after manual release, as defined by O-HOLD-INTERVAL, as the hold interval.
- Angular velocity projected on the fixed vertical axis, not on a tilted body-z axis.

The source asks for monitoring. It does not require a fixed yaw heading.

Derived from: cube.req.gnc

Allocation: cube.function.estimate-attitude

Verification method: test

Open items / 未解決事項:
- R-YAW.TBR.1: Decide whether 5 deg/s will become a limit. Define the sample rate and RMS calculation.

## cube.req.gnc: Control requirement set

`cube.req.gnc@requirements-review-20261115-3` · requirement_group · subsystem · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

This node groups requirements. It is not a separate test obligation.

Derived from: cube.req.system

## cube.req.mechanical: Mechanical requirement set

`cube.req.mechanical@requirements-review-20261115-3` · requirement_group · subsystem · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

This node groups requirements. It is not a separate test obligation.

Derived from: cube.req.system

## cube.req.operation: Operational requirement set

`cube.req.operation@requirements-review-20261115-3` · requirement_group · operational · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

This node groups requirements. It is not a separate test obligation.

Derived from: cube.req.system

## cube.req.system: System requirement set

`cube.req.system@requirements-review-20261115-3` · requirement_group · system · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

This node groups requirements. It is not a separate test obligation.

Derived from: M-VERTEX

## cube.req.verification: Verification platform requirement set

`cube.req.verification@requirements-review-20261115-3` · requirement_group · verification_platform · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

This node groups requirements. It is not a separate test obligation.

Derived from: cube.req.system
