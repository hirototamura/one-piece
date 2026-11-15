# Cube requirement review, 15 November 2026

Current model: `requirements-review-20261115-3`. This revision applies the user's
requirement-by-requirement comments to the previous eight-corner model.
The current set has 19 requirements, 7 classification groups and 3 separate
constraints. Existing numerical experiments and scoring retain their versions.

## Required behavior and operating interval

`M-VERTEX`, `R-HOLD`, `R-REPEAT` and `C-FIT-INSTALL` remain mandatory.
`R-HOLD` uses the common operating design value `O-HOLD-INTERVAL = 10 s`.
`R-DRIFT`, `R-RMS`, `R-TILT`, yaw monitoring and repeated hold tests use that
same interval. The 9-of-10 repetition rule retains its existing meaning.
The ten-second demonstration criterion does not establish indefinite holding.
The user's expectation of continued holding is recorded as a design assumption.

The total-tilt, RMS and drift requirements derive directly from `M-VERTEX`.
The five drive-limit obligations derive from `R-TILT` and `R-RMS`: usable
actuation within component limits supports the required balance performance.
Model comparison, synchronization and independent metrology derive from those
same system performance obligations because they provide their verification
capability. These are design/verification rationales, not measured causal results.
The organizational groups remain available for classification.

`R-MODEL` keeps its allocation to independent measurement and result evaluation.
`R-TRACE` moves to the explicit `cube.function.manage-configuration` function,
implemented in the model through the existing workstation/logger components.

## Requirements and constraints

- `C-FIT-MATERIAL` is retired from the requirement set. Print material remains a
  manufacturing design choice; no approved-material-list requirement is imposed.
- `C-FIT-PRINT` is a manufacturing constraint on each printed part in its planned
  orientation. It does not bound the assembled Cube envelope. Its direct
  parameter relationship to the whole-Cube `D-SIDE` is removed.
- `C-JAPAN` is retained as a manufacturing/procurement constraint.
- `C-BUDGET` is removed from the system requirements and retained only as a
  project constraint. Its unspecified budget is not treated as a performance score.
- `C-PRINT` remains a manufacturing-feasibility requirement as requested.

The specified printer is Bambu Lab A1. Its published build volume is
256 × 256 × 256 mm; actual part orientation and process clearance still need
checking. This is manufacturer specification data, not a physical measurement.
[Bambu Lab A1 official quick-start specification](https://cdn1.bambulab.com/documentation/quick-start-a75adcb1d5d5e/Quick%20Start%20Guide%20for%20A1.pdf).

## Corner identification and reference axes

`R-DETECT` requires automatic identification of the target support corner from
attitude/sensor information before balance control starts, for all eight corners.
The valid release conditions and ambiguous-corner handling remain open. The
identification algorithm and seven additional corner equilibria are not implemented
by changing a requirement or verification plan.

Yaw is rotation about the fixed world-vertical axis through the support vertex
at balance start, rather than about a subsequently tilted body-z axis. The initial
orientation sets the yaw reference; the existing requirement monitors yaw rate
and does not add a fixed-heading limit. A horizontal roll/pitch convention is
explicitly proposed: project initial body-x onto the horizontal plane for roll-x,
then use y = z × x for pitch-y. That horizontal convention remains visible for
review. Existing tilt slope angles are not relabelled as finite Euler angles.

The Explorer distinguishes requirements and constraints, shows the common
operating interval and reference axes, and preserves parameter trace links to
specific obligations or constraints. The operating value is separate from the
37 existing optimization/identification/fixed KDP records.

[Current statements](balancing_cube_requirements.md) · [Japanese](../ja/cube_requirements_review.md)
