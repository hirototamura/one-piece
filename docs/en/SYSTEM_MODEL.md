# One-Piece minimum system model

One-Piece is the single source of truth for requirements, Key Design Parameters, detailed model parameters, configurations, evidence and decisions. Human HTML and Engineering Agents consume the same versioned records. The balancing-cube project is in concept/development simulation.

## Graph contract

This small graph is inspired by SysML v2 requirements, structures, attributes and verification. It is not a SysML parser or standard API implementation. Nodes have stable IDs, revisions, kinds, product nodes, data and provenance. Edges pin a target ID and revision.

- `derive`: derived requirement → parent requirement.
- `satisfy`: design/product → intended requirement; correspondence, not proof of a pass.
- `verify`: verification/evidence → requirement/test case; evidence carries outcome and applicability.
- `allocate`: requirement/function/KDP → responsible product node.
- `constrain`: requirement/specification → constrained parameter/design.

Both directions are traversable. Requirements branch from mission to system, then to operational and subsystem requirements. The minimal product structure includes Cube, mechanics/actuation, sensing/estimation, control, power and the enabling verification platform.

## Source of truth and evidence

Append immutable JSON record revisions; reject changed content with an existing ID/revision. SQLite is a rebuildable index. Publish an import atomically only after validation. Preserve detailed model values, KDP units, uncertainty, model-path bindings and source approval state. Every run pins its requirements, model, controller and evaluation contract.

Assumptions remain assumptions and drafts remain drafts. Historical source labels do not establish new human approval. A numerical comparison reference is not an adopted baseline. Humans establish requirements, evaluation contracts and adopted baselines.

Verification concerns specified requirements; validation concerns intended purpose and environment. CPU/GPU agreement does not establish physical fidelity. A six-second numerical trial does not verify a thirty-second hardware hold requirement. Historical half-step evidence is retained, but new runs never perform half-step adjudication. Conditions already exposed to improvers are development-test feedback.

## Portable storage

Track compact canonical JSON in Git. Content-addressed evidence bundles carry databases, trajectories, HTML and video as GitHub Release assets. Release publication does not approve a requirement or design. Fetch verifies hashes, and the same pack restores offline. Reports are projections of records; LLMs read structured context instead of parsing HTML.

References: [NASA SE](../../.cursor/agents/nasa-se.md), [SpaceX-style SE](../../.cursor/agents/spacex-se.md), [OMG SysML v2](https://www.omg.org/spec/SysML/2.0/), [ENPIRE](https://arxiv.org/html/2606.19980v2).
