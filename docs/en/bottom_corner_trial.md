# Eight-corner mission and first trial

The user clarified the mission on 17 October 2026: balancing on each of the
Cube's eight corners. The first development trial uses corner `000` only.
English requirement statements are the source for the Japanese translations.
Formal wording remains draft. No adopted baseline or physical result is recorded.

## Canonical records

The current projection selects
`cube.simulation.snapshot@bottom-corner-000-20261017-3`. It pins 31 requirement/group
records and 38 KDP/parameter records. It derives from the English standards draft.
Earlier studies retain their exact requirement revisions, models and results.

- `M-VERTEX`: "The Cube shall balance on each of its 8 corners with its 3 reaction wheels."
- `R-FIRST-CORNER`: "The first development simulation shall evaluate the Cube on corner 000."
- `R-WHEEL-MOUNT-000`: "The first-trial model shall place its 3 reaction wheels on the faces incident to corner 000."
- `D-WHEEL-MOUNT-SIDE`: the fixed value `near_corner_000`, bound to `physics.wheel_mount_side`.

These records use revision `bottom-corner-000-20261017-3`. Their path is mission
→ system trial scope → subsystem mounting constraint. The mounting requirement
constrains the parameter and snapshot. A descendant design records intended
satisfaction. Numerical evidence verifies development test cases; planned
hardware cases are not verification evidence.

Corner 000 is the body origin. The Cube extends along the three positive axes.
Wheel centers are `(inset,s/2,s/2)` and the two axis permutations. The mounting
faces stay fixed. A future trial on another corner shall use the actual combined
center of mass to define its equilibrium. It shall not move the wheels implicitly
or assume that the corner-000 observation transform applies. The other seven
support-corner models are not implemented by this change.

## Controller and evidence

The provisional configuration retains the saved MASS controller from
`cube-f069bd6e148e43e0a411.candidate.10@1`. `controller_design_snapshot_ref` pins
its historical nominal design plant. Engineering Agents resolves that exact
source for later Q-weight changes. Multipliers remain relative to source Q;
omitted settings retain saved design parameters.

`cube.analysis.bottom000.mounting-2x2@1` records four matched mounting/controller
combinations and a later reference-specific controller test.
`cube.analysis.bottom000.current-controller@1` records the retained MASS
controller with lower mounts: 12/12 disclosed development cases passed.
Its score was 0.988586, below the earlier upper-mount MASS score of 0.991612.
Two rebuilt LQR alternatives passed 9/12 and 8/12 lower-mount cases. Lower center
of mass did not guarantee better control performance.

These six-second numerical tests do not verify the eight-corner hardware
mission, draft thirty-second hold or physical fidelity. Fresh confirmation is
separate. Preparation revisions remain immutable and superseded in the current view.

## Verification platform

Qwen/vLLM uses GPUs 0–5 as three replicas, each with tensor-parallel size 2.
MJX uses GPUs 6–7. Native MuJoCo uses CPUs. Deployment probes and native
MuJoCo–MJX agreement are platform evidence, not physical validation. Selective
comparison in the design-loop runner remains future implementation work.

[Japanese translation](../ja/bottom_corner_trial.md).
