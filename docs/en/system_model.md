# One-Piece minimum system model

One-Piece is the single source of truth for requirements, Key Design Parameters, detailed model parameters, configurations, evidence and decisions. Human HTML and Engineering Agents consume the same versioned records. The balancing-cube project is in concept/development simulation.

## Graph contract

This small graph uses an [OMG Systems Modeling API 1.0 boundary](sysml_api.md) for ProjectService Read and ElementNavigationService. It preserves the source graph as standard annotations and named Dependencies. It is not a SysML parser or a complete native SysML semantic transformation. Nodes have stable IDs, revisions, kinds, product nodes, data and provenance. Edges pin a target ID and revision.

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

Automated requirement verification and Git-like model diffs are mandatory platform capabilities. A change must identify affected verification cases and retain the applicability of each result to exact source revisions. Existing integrity checks and the HTML design comparison cover part of this intent. See [scope and proposed acceptance criteria](verification_and_diff.md) for the remaining verification execution, semantic diff and re-execution work.

Track compact canonical JSON in Git. Content-addressed evidence bundles carry databases, trajectories, HTML and video as GitHub Release assets. Release publication does not approve a requirement or design. Fetch verifies hashes, and the same pack restores offline. Reports are projections of records; LLMs read structured context instead of parsing HTML.

Project-scoped `check` and `bundle` require the selected project's artifacts; use an unscoped `check` to audit every project's evidence. Metadata-only clones can be restored repeatedly, including after another Git clone, without rewriting canonical records. Bundles store unusually compressible entries uncompressed so that valid evidence also respects the import expansion-ratio guard.

References: [NASA SE](../engineering/nasa_se.md), [SpaceX-style SE](../engineering/spacex_se.md), [OMG SysML v2](https://www.omg.org/spec/SysML/2.0/), [ENPIRE](https://arxiv.org/html/2606.19980v2).

Current balancing-cube projections use `cube.simulation.snapshot@fixed-dt-mvp-2` via an explicit active system-model reference. The comparison design and campaign summary are mandatory outside context limits. Requirement statement status is separate from physical verification; `hardware_verification_required` is a planned hardware evidence obligation, not a pass flag. Numerical evaluations verify development test cases. Historical revisions retain their original fields and links for audit.
