# Balancing Cube requirement drafts

This view comes from canonical JSON at `standards-draft-20261011-2`. Regenerate it with `python projects/balancing-cube/migrate_standards.py --write-docs`.

The English text is the source. The Japanese text is its translation. All revised statements are drafts that need human review.

Priority: ISO/IEC/IEEE 29148:2018 first; NASA systems engineering standards and requirements guidance second; ASD-STE100 Issue 9 third where compatible.
Normative requirement modal: `shall`. NASA Appendix C identifies shall as the requirement modal. ASD-STE100 Issue 9 lists shall as unapproved and must as its alternative; the declared priority governs this choice.
Apply compatible ASD-STE100 rules for active voice, defined technical names and sentence length. The full ISO text was not available for a clause audit; a complete STE dictionary audit and standards certification have not been performed.

The 7 organizational containers are not separate test obligations. The 22 obligations include 8 atomic children of the original compound requirements.
Verification cases are plans only. There are no new hardware results. Historical numerical evidence retains its original revision targets.

See [writing standards](../engineering/standards.md), [system model](system_model.md) and [API scope](sysml_api.md).

## cube.req.system: System requirement set

`cube.req.system@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

This node groups requirements. It is not a separate test obligation.

cube.req.operation, cube.req.mechanical, cube.req.gnc, cube.req.verification, R-DRIVE, R-TILT, R-RMS, R-DRIFT

## cube.req.operation: Operational requirement set

`cube.req.operation@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

This node groups requirements. It is not a separate test obligation.

R-HOLD, R-REPEAT

## cube.req.mechanical: Mechanical requirement set

`cube.req.mechanical@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

This node groups requirements. It is not a separate test obligation.

C-FIT, C-JAPAN, C-PRINT, C-BUDGET

## cube.req.gnc: Control requirement set

`cube.req.gnc@standards-draft-20261011-2` · `cube.gnc` · `draft` · `not_run`

This node groups requirements. It is not a separate test obligation.

R-YAW

## cube.req.verification: Verification platform requirement set

`cube.req.verification@standards-draft-20261011-2` · `cube.verification` · `draft` · `not_run`

This node groups requirements. It is not a separate test obligation.

R-VISION, R-SYNC, R-MODEL, R-TRACE

## C-FIT: Manufacturing and installation requirement set

`C-FIT@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

This node groups requirements. It is not a separate test obligation.

C-FIT-PRINT, C-FIT-MATERIAL, C-FIT-INSTALL

## R-DRIVE: Drive limit requirement set

`R-DRIVE@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

This node groups requirements. It is not a separate test obligation.

R-DRIVE-TORQUE, R-DRIVE-SPEED, R-DRIVE-TEMP, R-DRIVE-VOLTAGE, R-DRIVE-CURRENT

## M-VERTEX: Vertex hold mission

`M-VERTEX@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

The Cube shall hold its vertex position with 3 reaction wheels in the physical test environment.

This mission requires a physical demonstration of the Cube concept.


Acceptance: {"domain": "hardware", "metric": "vertex_hold_demonstrated", "operator": "==", "unit": "1", "value": true}

Verification method: test

Source statement status: confirmed

- `M-VERTEX.TBR.1`: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

Source: `M-VERTEX@trace-20261010-2`; SHA-256 `4799937318ed4f7404c2cee216a46f84f04fab3d9b215fc0a964588190ae652d`.

## C-JAPAN: Component supply to Japan

`C-JAPAN@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

The Cube shall use components that suppliers can supply to Japan.

The user needs to obtain parts in Japan.


Acceptance: {"metric": "components_available_for_supply_to_japan", "operator": "==", "unit": "1", "value": "all_purchased_components"}

Verification method: inspection

Source statement status: confirmed

- `C-JAPAN.TBR.1`: Define acceptable lead time and supply cost. The source word 'easy' has no numerical limit.

Source: `C-JAPAN@trace-20261010-2`; SHA-256 `a30d6923b8b4218c9a9713f23f4f1c52982e7c89dc49c850aa8ebb7575487a13`.

## C-PRINT: Housing manufacture

`C-PRINT@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

The Cube housing shall be a part that the specified 3D printer can make.

The user intends to use a friend's 3D printer.


Acceptance: {"metric": "housing_manufacturable", "operator": "==", "requirement_ref": {"id": "C-FIT-PRINT", "revision": "standards-draft-20261011-2"}, "unit": "1", "value": true}

Verification method: demonstration

Source statement status: confirmed

- `C-PRINT.TBR.1`: Identify the specified printer, material and print settings.

Source: `C-PRINT@trace-20261010-2`; SHA-256 `e926acac7b34ad0bae42e8af5b332e5ef4462ebf90f047f9fc67285da2627b6e`.

## C-BUDGET: First prototype cost

`C-BUDGET@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

The cost of the first Cube prototype shall be no more than the approved budget.

The prototype needs an explicit cost limit.


Acceptance: {"limit_ref": {"id": "D-BUDGET", "revision": "standards-draft-20261011-2"}, "metric": "prototype_cost", "operator": "<=", "unit": "JPY"}

Verification method: analysis

Source statement status: draft

- `C-BUDGET.TBR.1`: Set the budget and cost scope. D-BUDGET has no value.

Source: `C-BUDGET@trace-20261010-2`; SHA-256 `a1fd01730722f6c6718dd3b5f407302457f30c889412198ffefb58a3647b24cc`.

## R-HOLD: Hold after manual release

`R-HOLD@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

After manual placement and release, the Cube shall hold its vertex position for at least 30 s without external support.

The first prototype starts from manual placement. Automatic stand-up is outside this draft scope.

Condition: Use the first 30 s after manual release as the hold interval.

Acceptance: {"domain": "hardware", "metric": "unsupported_vertex_hold_duration", "operator": ">=", "unit": "s", "value": 30}

Verification method: test

Source statement status: draft

- `R-HOLD.TBR.1`: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

Source: `R-HOLD@trace-20261010-2`; SHA-256 `f0fcce1b22e2d58b3463a9882ed9a8bbccf720bc6657da40a42a3f20b2a5c0cf`.

## R-TILT: Maximum tilt angle

`R-TILT@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

During the hold interval, the Cube shall keep its tilt angle no more than 5 deg.

This limit describes the Cube performance during the hardware hold test.

Condition: Use the first 30 s after manual release as the hold interval.

Acceptance: {"domain": "hardware", "metric": "peak_tilt_angle", "operator": "<=", "unit": "deg", "value": 5}

Verification method: test

Source statement status: draft

- `R-TILT.TBR.1`: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

Source: `R-TILT@trace-20261010-2`; SHA-256 `b4a542e2c2f5cebfa4deaa111a9bda7e1fea97d68dead7b743f5618913873a76`.

## R-RMS: Tilt angle RMS

`R-RMS@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

During the hold interval, the Cube shall have a tilt angle RMS no more than 2 deg.

This limit describes the Cube performance during the hardware hold test.

Condition: Use the first 30 s after manual release as the hold interval.

Acceptance: {"domain": "hardware", "metric": "tilt_angle_rms", "operator": "<=", "unit": "deg", "value": 2}

Verification method: test

Source statement status: draft

- `R-RMS.TBR.1`: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

Source: `R-RMS@trace-20261010-2`; SHA-256 `2ceec81d22e96442798bf229832d6eda67871b3b78fa2a546c84353595325500`.

## R-DRIFT: Contact point movement

`R-DRIFT@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

During the hold interval, the Cube contact point shall move no more than 2 mm from its initial position.

This limit describes the Cube performance during the hardware hold test.

Condition: Use the first 30 s after manual release as the hold interval.

Acceptance: {"domain": "hardware", "metric": "peak_contact_point_displacement", "operator": "<=", "unit": "mm", "value": 2}

Verification method: test

Source statement status: draft

- `R-DRIFT.TBR.1`: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

Source: `R-DRIFT@trace-20261010-2`; SHA-256 `7eab0b2b715e5047db9905d881508a7a862b328e3824003a1d247385abe58968`.

## R-REPEAT: Repeated hold tests

`R-REPEAT@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

Under fixed test conditions, the Cube shall pass the hold test in at least 9 of 10 trials.

Repeated trials check repeatability for the stated test conditions.


Acceptance: {"domain": "hardware", "metric": "successful_hold_trials", "operator": ">=", "sample_count": 10, "unit": "trials/10", "value": 9}

Verification method: test

Source statement status: draft

- `R-REPEAT.TBR.1`: Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.

- `R-REPEAT.TBR.2`: Define trial order, resets and the complete hold-test pass rule before testing.

Source: `R-REPEAT@trace-20261010-2`; SHA-256 `3af5a6d2e1248bee831cfb28d5f6f5ce14a728987cabdfc4970c63cdf250e8d1`.

## R-YAW: Yaw rate monitoring

`R-YAW@standards-draft-20261011-2` · `cube.gnc` · `draft` · `not_run`

During the hold interval, the control system shall monitor the yaw rate RMS.

The source asks for monitoring. It does not require a fixed yaw heading.

Condition: Use the first 30 s after manual release as the hold interval.

Acceptance: {"metric": "yaw_rate_rms_recorded", "operator": "==", "target_only": {"unit": "deg/s", "value": 5}, "unit": "1", "value": true}

Verification method: test

Source statement status: draft

- `R-YAW.TBR.1`: Decide whether 5 deg/s will become a limit. Define the sample rate and RMS calculation.

Source: `R-YAW@trace-20261010-2`; SHA-256 `05910a799d4afe495aedfc265b6832f5a6e62365bfb7a98b6430589ee81e1c41`.

## R-VISION: Independent attitude measurement

`R-VISION@standards-draft-20261011-2` · `cube.verification` · `draft` · `not_run`

The independent attitude measurement system shall have an angular standard uncertainty of no more than 0.5 deg.

An independent measurement checks the attitude estimate used by the Cube.


Acceptance: {"domain": "hardware", "metric": "attitude_standard_uncertainty", "operator": "<=", "unit": "deg", "value": 0.5}

Verification method: test

Source statement status: draft

- `R-VISION.TBR.1`: Define the attitude components, calibration method and uncertainty calculation. This draft uses standard uncertainty.

Source: `R-VISION@trace-20261010-2`; SHA-256 `c8d56c9806b3af8fd91bda34f31fc689ab3daaeaa8f761a075d2e0a804f17f99`.

## R-SYNC: Video and MCU time relation

`R-SYNC@standards-draft-20261011-2` · `cube.verification` · `draft` · `not_run`

The verification platform shall calculate the time relation between video and MCU timestamps with a time uncertainty no more than 0.005 s.

A known time relation is necessary to compare independent measurements and controller logs.


Acceptance: {"domain": "hardware", "metric": "video_mcu_time_uncertainty", "operator": "<=", "unit": "s", "value": 0.005}

Verification method: test

Source statement status: draft

- `R-SYNC.TBR.1`: Define the time uncertainty and calibration method. A 60 frame/s video alone does not demonstrate 0.005 s.

Source: `R-SYNC@trace-20261010-2`; SHA-256 `8312021ccda4e9af192f732206a41e34ae46eb83cd60f9409c3f099dca5ce96f`.

## R-MODEL: Independent model comparison

`R-MODEL@standards-draft-20261011-2` · `cube.verification` · `draft` · `not_run`

The verification platform shall compare model results with independent physical measurements under the same test conditions.

CPU and GPU agreement checks numerical behavior. Physical measurements are necessary to assess model error.


Acceptance: {"domain": "hardware_model_comparison", "metric": "model_error", "operator": "<=", "unit": "defined_per_quantity", "value": null}

Verification method: analysis

Source statement status: draft

- `R-MODEL.TBR.1`: Define comparison quantities, units, error limits and independent physical data before a pass decision.

Source: `R-MODEL@trace-20261010-2`; SHA-256 `f3f7fa2059d2740844b4b22c5e81f323b316636c9848c3f400f958000a56997b`.

## R-TRACE: Exact run references

`R-TRACE@standards-draft-20261011-2` · `cube.verification` · `draft` · `not_run`

The verification platform shall identify the exact revisions of requirements, KDPs, designs, conditions, and results for each run.

Exact references make changes and evidence applicability visible.


Acceptance: {"metric": "missing_or_ambiguous_revision_references", "operator": "==", "unit": "count", "value": 0}

Verification method: inspection

Source statement status: confirmed

Source: `R-TRACE@trace-20261010-2`; SHA-256 `5d961ba1f586672fa4d92e60a94a6978f8c2d5b523564caf13444dca46398cbf`.

## R-DRIVE-TORQUE: Motor torque limits

`R-DRIVE-TORQUE@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

At each measured speed, each motor shall have torque between its approved minimum and maximum limits.

This obligation is one part of the original compound drive requirement.


Acceptance: {"domain": "hardware", "limits_status": "unresolved", "metric": "motor_torque_envelope_exceeded", "operator": "==", "unit": "1", "value": false}

Verification method: test

Source statement status: draft

- `R-DRIVE-TORQUE.TBR.1`: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

Source: `R-DRIVE@trace-20261010-2`; SHA-256 `5f55625c658011d360d978b465484866f85152b9fb3a7a46960d75072d6e264e`.

## R-DRIVE-SPEED: Wheel speed limits

`R-DRIVE-SPEED@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

Each reaction wheel shall have a speed magnitude no more than the approved limit for its assembly.

This obligation is one part of the original compound drive requirement.


Acceptance: {"domain": "hardware", "limits_status": "unresolved", "metric": "wheel_speed_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Verification method: test

Source statement status: draft

- `R-DRIVE-SPEED.TBR.1`: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

Source: `R-DRIVE@trace-20261010-2`; SHA-256 `5f55625c658011d360d978b465484866f85152b9fb3a7a46960d75072d6e264e`.

## R-DRIVE-TEMP: Component temperature limits

`R-DRIVE-TEMP@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

Each motor and driver shall have a temperature between its approved minimum and maximum limits.

This obligation is one part of the original compound drive requirement.


Acceptance: {"domain": "hardware", "limits_status": "unresolved", "metric": "component_temperature_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Verification method: test

Source statement status: draft

- `R-DRIVE-TEMP.TBR.1`: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

Source: `R-DRIVE@trace-20261010-2`; SHA-256 `5f55625c658011d360d978b465484866f85152b9fb3a7a46960d75072d6e264e`.

## R-DRIVE-VOLTAGE: Bus voltage limits

`R-DRIVE-VOLTAGE@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

The drive system shall keep the bus voltage between the approved minimum and maximum limits of each connected component.

This obligation is one part of the original compound drive requirement.


Acceptance: {"domain": "hardware", "limits_status": "unresolved", "metric": "bus_voltage_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Verification method: test

Source statement status: draft

- `R-DRIVE-VOLTAGE.TBR.1`: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

Source: `R-DRIVE@trace-20261010-2`; SHA-256 `5f55625c658011d360d978b465484866f85152b9fb3a7a46960d75072d6e264e`.

## R-DRIVE-CURRENT: Bus current limits

`R-DRIVE-CURRENT@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

The drive system shall keep the bus current between the approved minimum and maximum limits of the bus circuit.

This obligation is one part of the original compound drive requirement.


Acceptance: {"domain": "hardware", "limits_status": "unresolved", "metric": "bus_current_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Verification method: test

Source statement status: draft

- `R-DRIVE-CURRENT.TBR.1`: Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.

- `R-DRIVE-CURRENT.TBR.2`: Define the bus circuit ratings. Bus current does not show each motor winding current.

Source: `R-DRIVE@trace-20261010-2`; SHA-256 `5f55625c658011d360d978b465484866f85152b9fb3a7a46960d75072d6e264e`.

## C-FIT-PRINT: Printed part dimensions

`C-FIT-PRINT@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

Each printed housing part shall have dimensions no more than the specified build limits of the 3D printer.

This obligation is one part of the original compound manufacturing requirement.


Acceptance: {"limits_status": "unresolved", "metric": "printed_parts_inside_build_volume", "operator": "==", "unit": "1", "value": true}

Verification method: inspection

Source statement status: draft

- `C-FIT-PRINT.TBR.1`: Identify printer limits, the material list, component dimensions and required movement clearance.

Source: `C-FIT@trace-20261010-2`; SHA-256 `521cf3051c08776477a9bf539ed2b263c2e4c269dd4efb4502c9914b3da5e074`.

## C-FIT-MATERIAL: Print material selection

`C-FIT-MATERIAL@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

The Cube housing shall use a print material from the approved material list for the specified 3D printer.

This obligation is one part of the original compound manufacturing requirement.


Acceptance: {"limits_status": "unresolved", "metric": "material_on_printer_material_list", "operator": "==", "unit": "1", "value": true}

Verification method: inspection

Source statement status: draft

- `C-FIT-MATERIAL.TBR.1`: Identify printer limits, the material list, component dimensions and required movement clearance.

Source: `C-FIT@trace-20261010-2`; SHA-256 `521cf3051c08776477a9bf539ed2b263c2e4c269dd4efb4502c9914b3da5e074`.

## C-FIT-INSTALL: Installed component dimensions

`C-FIT-INSTALL@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

Each installed component shall have dimensions no more than the specified dimensions of its space in the Cube housing.

This obligation is one part of the original compound manufacturing requirement.


Acceptance: {"limits_status": "unresolved", "metric": "installed_components_inside_assigned_space", "operator": "==", "unit": "1", "value": true}

Verification method: inspection

Source statement status: draft

- `C-FIT-INSTALL.TBR.1`: Identify printer limits, the material list, component dimensions and required movement clearance.

Source: `C-FIT@trace-20261010-2`; SHA-256 `521cf3051c08776477a9bf539ed2b263c2e4c269dd4efb4502c9914b3da5e074`.
