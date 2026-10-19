# Balancing Cube reviewed requirements

`reviewed-20261019-1` · human review: 2026-10-19 · reviewer: hirototamura

The human accepted the requirement wording and the function/component allocation split. Verification results, unresolved items and historical evidence retain their separate states.

Canonical baseline: `cube.baseline.requirements-allocation@reviewed-20261019-1`.

There are 22 obligations and 7 organizational groups. Open numerical limits and verification procedures remain open; review is not a hardware pass.

Regenerate: `python projects/balancing-cube/review_requirements.py --write-docs`.

## C-BUDGET: First prototype cost

`C-BUDGET@reviewed-20261019-1` · reviewed · human_reviewed · not_run

The cost of the first Cube prototype shall be no more than the approved budget.

The prototype needs an explicit cost limit.

Acceptance / 合否基準: {"limit_ref": {"id": "D-BUDGET", "revision": "reviewed-20261019-1"}, "metric": "prototype_cost", "operator": "<=", "unit": "JPY"}

Allocation: cube.system

Open items / 未解決事項:
- C-BUDGET.TBR.1: Set the budget and cost scope. D-BUDGET has no value.

## C-FIT: Manufacturing and installation requirement set

`C-FIT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

This node groups requirements. It is not a separate test obligation.

## C-FIT-INSTALL: Installed component dimensions

`C-FIT-INSTALL@reviewed-20261019-1` · reviewed · human_reviewed · not_run

Each installed component shall have dimensions no more than the specified dimensions of its space in the Cube housing.

This obligation is one part of the original compound manufacturing requirement.

Acceptance / 合否基準: {"limits_status": "unresolved", "metric": "installed_components_inside_assigned_space", "operator": "==", "unit": "1", "value": true}

Allocation: cube.component.frame-housing, cube.component.reaction-wheels, cube.component.motor-drivers, cube.component.imu, cube.component.controller, cube.component.power-bus

Open items / 未解決事項:
- C-FIT-INSTALL.TBR.1: Identify printer limits, the material list, component dimensions and required movement clearance.

## C-FIT-MATERIAL: Print material selection

`C-FIT-MATERIAL@reviewed-20261019-1` · reviewed · human_reviewed · not_run

The Cube housing shall use a print material from the approved material list for the specified 3D printer.

This obligation is one part of the original compound manufacturing requirement.

Acceptance / 合否基準: {"limits_status": "unresolved", "metric": "material_on_printer_material_list", "operator": "==", "unit": "1", "value": true}

Allocation: cube.component.frame-housing

Open items / 未解決事項:
- C-FIT-MATERIAL.TBR.1: Identify printer limits, the material list, component dimensions and required movement clearance.

## C-FIT-PRINT: Printed part dimensions

`C-FIT-PRINT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

Each printed housing part shall have dimensions no more than the specified build limits of the 3D printer.

This obligation is one part of the original compound manufacturing requirement.

Acceptance / 合否基準: {"limits_status": "unresolved", "metric": "printed_parts_inside_build_volume", "operator": "==", "unit": "1", "value": true}

Allocation: cube.component.frame-housing

Open items / 未解決事項:
- C-FIT-PRINT.TBR.1: Identify printer limits, the material list, component dimensions and required movement clearance.

## C-JAPAN: Component supply to Japan

`C-JAPAN@reviewed-20261019-1` · reviewed · human_reviewed · not_run

The Cube shall use components that suppliers can supply to Japan.

The user needs to obtain parts in Japan.

Acceptance / 合否基準: {"metric": "components_available_for_supply_to_japan", "operator": "==", "unit": "1", "value": "all_purchased_components"}

Allocation: cube.component.frame-housing, cube.component.vertex-contact, cube.component.reaction-wheels, cube.component.motor-drivers, cube.component.imu, cube.component.controller, cube.component.power-bus

Open items / 未解決事項:
- C-JAPAN.TBR.1: Define acceptable lead time and supply cost. The source word 'easy' has no numerical limit.

## C-PRINT: Housing manufacture

`C-PRINT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

The Cube housing shall be a part that the specified 3D printer can make.

The user intends to use a friend's 3D printer.

Acceptance / 合否基準: {"metric": "housing_manufacturable", "operator": "==", "requirement_ref": {"id": "C-FIT-PRINT", "revision": "reviewed-20261019-1"}, "unit": "1", "value": true}

Allocation: cube.component.frame-housing

Open items / 未解決事項:
- C-PRINT.TBR.1: Identify the specified printer, material and print settings.

## M-VERTEX: Vertex hold mission

`M-VERTEX@reviewed-20261019-1` · reviewed · human_reviewed · not_run

The Cube shall hold its vertex position with 3 reaction wheels in the physical test environment.

This mission requires a physical demonstration of the Cube concept.

Acceptance / 合否基準: {"domain": "hardware", "metric": "vertex_hold_demonstrated", "operator": "==", "unit": "1", "value": true}

Allocation: cube.system

Open items / 未解決事項:
- M-VERTEX.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

## R-DRIFT: Contact point movement

`R-DRIFT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

During the hold interval, the Cube contact point shall move no more than 2 mm from its initial position.

This limit describes the Cube performance during the hardware hold test.

Acceptance / 合否基準: {"domain": "hardware", "metric": "peak_contact_point_displacement", "operator": "<=", "unit": "mm", "value": 2}

Allocation: cube.function.control-balance, cube.function.maintain-contact

Open items / 未解決事項:
- R-DRIFT.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

## R-DRIVE: Drive limit requirement set

`R-DRIVE@reviewed-20261019-1` · reviewed · human_reviewed · not_run

This node groups requirements. It is not a separate test obligation.

## R-DRIVE-CURRENT: Bus current limits

`R-DRIVE-CURRENT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

The drive system shall keep the bus current between the approved minimum and maximum limits of the bus circuit.

This obligation is one part of the original compound drive requirement.

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "bus_current_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Allocation: cube.function.manage-power

Open items / 未解決事項:
- R-DRIVE-CURRENT.TBR.1: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.
- R-DRIVE-CURRENT.TBR.2: Define the bus circuit ratings. Bus current does not show each motor winding current.

## R-DRIVE-SPEED: Wheel speed limits

`R-DRIVE-SPEED@reviewed-20261019-1` · reviewed · human_reviewed · not_run

Each reaction wheel shall have a speed magnitude no more than the approved limit for its assembly.

This obligation is one part of the original compound drive requirement.

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "wheel_speed_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Allocation: cube.function.generate-torque

Open items / 未解決事項:
- R-DRIVE-SPEED.TBR.1: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

## R-DRIVE-TEMP: Component temperature limits

`R-DRIVE-TEMP@reviewed-20261019-1` · reviewed · human_reviewed · not_run

Each motor and driver shall have a temperature between its approved minimum and maximum limits.

This obligation is one part of the original compound drive requirement.

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "component_temperature_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Allocation: cube.function.manage-power

Open items / 未解決事項:
- R-DRIVE-TEMP.TBR.1: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

## R-DRIVE-TORQUE: Motor torque limits

`R-DRIVE-TORQUE@reviewed-20261019-1` · reviewed · human_reviewed · not_run

At each measured speed, each motor shall have torque between its approved minimum and maximum limits.

This obligation is one part of the original compound drive requirement.

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "motor_torque_envelope_exceeded", "operator": "==", "unit": "1", "value": false}

Allocation: cube.function.generate-torque

Open items / 未解決事項:
- R-DRIVE-TORQUE.TBR.1: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

## R-DRIVE-VOLTAGE: Bus voltage limits

`R-DRIVE-VOLTAGE@reviewed-20261019-1` · reviewed · human_reviewed · not_run

The drive system shall keep the bus voltage between the approved minimum and maximum limits of each connected component.

This obligation is one part of the original compound drive requirement.

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "bus_voltage_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Allocation: cube.function.manage-power

Open items / 未解決事項:
- R-DRIVE-VOLTAGE.TBR.1: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

## R-HOLD: Hold after manual release

`R-HOLD@reviewed-20261019-1` · reviewed · human_reviewed · not_run

After manual placement and release, the Cube shall hold its vertex position for at least 30 s without external support.

The first prototype starts from manual placement. Automatic stand-up is outside this draft scope.

Acceptance / 合否基準: {"domain": "hardware", "metric": "unsupported_vertex_hold_duration", "operator": ">=", "unit": "s", "value": 30}

Allocation: cube.function.control-balance, cube.function.maintain-contact

Open items / 未解決事項:
- R-HOLD.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

## R-MODEL: Independent model comparison

`R-MODEL@reviewed-20261019-1` · reviewed · human_reviewed · not_run

The verification platform shall compare model results with independent physical measurements under the same test conditions.

CPU and GPU agreement checks numerical behavior. Physical measurements are necessary to assess model error.

Acceptance / 合否基準: {"domain": "hardware_model_comparison", "metric": "model_error", "operator": "<=", "unit": "defined_per_quantity", "value": null}

Allocation: cube.function.measure-motion, cube.function.evaluate-trace

Open items / 未解決事項:
- R-MODEL.TBR.1: Define comparison quantities, units, error limits and independent physical data before a pass decision.

## R-REPEAT: Repeated hold tests

`R-REPEAT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

Under fixed test conditions, the Cube shall pass the hold test in at least 9 of 10 trials.

Repeated trials check repeatability for the stated test conditions.

Acceptance / 合否基準: {"domain": "hardware", "metric": "successful_hold_trials", "operator": ">=", "sample_count": 10, "unit": "trials/10", "value": 9}

Allocation: cube.function.control-balance, cube.function.evaluate-trace

Open items / 未解決事項:
- R-REPEAT.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.
- R-REPEAT.TBR.2: Define trial order, resets and the complete hold-test pass rule before testing.

## R-RMS: Tilt angle RMS

`R-RMS@reviewed-20261019-1` · reviewed · human_reviewed · not_run

During the hold interval, the Cube shall have a tilt angle RMS no more than 2 deg.

This limit describes the Cube performance during the hardware hold test.

Acceptance / 合否基準: {"domain": "hardware", "metric": "tilt_angle_rms", "operator": "<=", "unit": "deg", "value": 2}

Allocation: cube.function.control-balance

Open items / 未解決事項:
- R-RMS.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

## R-SYNC: Video and MCU time relation

`R-SYNC@reviewed-20261019-1` · reviewed · human_reviewed · not_run

The verification platform shall calculate the time relation between video and MCU timestamps with a time uncertainty no more than 0.005 s.

A known time relation is necessary to compare independent measurements and controller logs.

Acceptance / 合否基準: {"domain": "hardware", "metric": "video_mcu_time_uncertainty", "operator": "<=", "unit": "s", "value": 0.005}

Allocation: cube.function.capture-synchronize

Open items / 未解決事項:
- R-SYNC.TBR.1: Define the time uncertainty and calibration method. A 60 frame/s video alone does not demonstrate 0.005 s.

## R-TILT: Maximum tilt angle

`R-TILT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

During the hold interval, the Cube shall keep its tilt angle no more than 5 deg.

This limit describes the Cube performance during the hardware hold test.

Acceptance / 合否基準: {"domain": "hardware", "metric": "peak_tilt_angle", "operator": "<=", "unit": "deg", "value": 5}

Allocation: cube.function.control-balance, cube.function.maintain-contact

Open items / 未解決事項:
- R-TILT.TBR.1: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

## R-TRACE: Exact run references

`R-TRACE@reviewed-20261019-1` · reviewed · human_reviewed · not_run

The verification platform shall identify the exact revisions of requirements, KDPs, designs, conditions, and results for each run.

Exact references make changes and evidence applicability visible.

Acceptance / 合否基準: {"metric": "missing_or_ambiguous_revision_references", "operator": "==", "unit": "count", "value": 0}

Allocation: cube.function.capture-synchronize, cube.function.evaluate-trace

## R-VISION: Independent attitude measurement

`R-VISION@reviewed-20261019-1` · reviewed · human_reviewed · not_run

The independent attitude measurement system shall have an angular standard uncertainty of no more than 0.5 deg.

An independent measurement checks the attitude estimate used by the Cube.

Acceptance / 合否基準: {"domain": "hardware", "metric": "attitude_standard_uncertainty", "operator": "<=", "unit": "deg", "value": 0.5}

Allocation: cube.function.measure-motion

Open items / 未解決事項:
- R-VISION.TBR.1: Define the attitude components, calibration method and uncertainty calculation. This draft uses standard uncertainty.

## R-YAW: Yaw rate monitoring

`R-YAW@reviewed-20261019-1` · reviewed · human_reviewed · not_run

During the hold interval, the control system shall monitor the yaw rate RMS.

The source asks for monitoring. It does not require a fixed yaw heading.

Acceptance / 合否基準: {"metric": "yaw_rate_rms_recorded", "operator": "==", "target_only": {"unit": "deg/s", "value": 5}, "unit": "1", "value": true}

Allocation: cube.function.estimate-attitude

Open items / 未解決事項:
- R-YAW.TBR.1: Decide whether 5 deg/s will become a limit. Define the sample rate and RMS calculation.

## cube.req.gnc: Control requirement set

`cube.req.gnc@reviewed-20261019-1` · reviewed · human_reviewed · not_run

This node groups requirements. It is not a separate test obligation.

## cube.req.mechanical: Mechanical requirement set

`cube.req.mechanical@reviewed-20261019-1` · reviewed · human_reviewed · not_run

This node groups requirements. It is not a separate test obligation.

## cube.req.operation: Operational requirement set

`cube.req.operation@reviewed-20261019-1` · reviewed · human_reviewed · not_run

This node groups requirements. It is not a separate test obligation.

## cube.req.system: System requirement set

`cube.req.system@reviewed-20261019-1` · reviewed · human_reviewed · not_run

This node groups requirements. It is not a separate test obligation.

## cube.req.verification: Verification platform requirement set

`cube.req.verification@reviewed-20261019-1` · reviewed · human_reviewed · not_run

This node groups requirements. It is not a separate test obligation.
