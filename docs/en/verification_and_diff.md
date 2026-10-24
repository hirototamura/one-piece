# Automated requirement verification and model diffs

The user identified both capabilities as mandatory on 2026-10-11. The [competitor study](competitor_tradeoff.md) supplies context. Its old adoption decisions are not a source of requirements. The detailed acceptance criteria below are design proposals, not implemented features or adopted engineering baselines. Formal project requirements shall use the canonical versioned JSON record contract after review. These notes do not create a second requirement store.

Use [ISO/IEC/IEEE 29148:2018 first, followed by NASA standards and then compatible ASD-STE100 guidance](../engineering/standards.md). A requirement's source status, a test outcome, and a human baseline decision are separate facts.

## Automated requirement verification

The intended flow is:

`changed configuration → affected verification cases → bounded execution → deterministic evaluation → versioned evidence → requirement applicability`

One-Piece shall retain the requirement revision, verification case, evaluation rules, execution configuration and evidence. Engineering Agents shall execute the registered test adapter in its budget. A test adapter may call MuJoCo or another approved analysis tool. A requirement ID or an LLM-generated sentence alone shall not select an executable command.

Proposed acceptance criteria:

- Each result identifies the exact requirement, test case, model, controller, evaluation rules, input digest and evaluator version.
- The evaluator checks values, units, limits, duration and required conditions. LLM text cannot override its outcome.
- Record `pass`, `fail`, `not_run`, `inconclusive` and `error` separately. A missing GPU, invalid unit, incomplete run or missing evidence cannot produce `pass`.
- A result is applicable only to its recorded configuration and test scope. A six-second simulation does not satisfy a thirty-second hardware requirement. Simulation agreement and physical validation remain separate.
- A changed requirement, limit, model, controller or evaluator makes the old result pending an applicability check. Preserve the old result and its original revision links.
- Human and agent views derive requirement coverage from the same records. Uncovered conditions remain visible. Importing evidence never creates an adopted baseline.

The minimum demonstration shall include one passing case, one failing case, one missing input, and one changed limit that requires a new evaluation. It shall retain the prior result and prove that it does not become evidence for the changed requirement automatically. Simulations need re-execution when physical inputs change. A threshold-only change may permit re-evaluation of retained measurements if their coverage and provenance remain sufficient. Record that choice and its reason.

## Git-like changes and semantic diffs

Git shall retain the source history. The model comparison shall identify the meaning of each change, beyond a line diff of JSON.

Proposed acceptance criteria:

- Select exact before/after configurations. A model configuration is a manifest of record IDs, revisions and content hashes. Keep that manifest distinct from a Git commit and from a SysML API publication Commit.
- Report added, removed and changed requirements, KDPs, detailed parameters, evaluation rules, graph edges and artifact references.
- Each changed field retains its JSON path, old value and new value. Include units, approval state and exact link revisions. Treat absent and null values as different states.
- Preserve direction and endpoint revisions for graph edges. Separate ordering-only differences from semantic changes without losing meaningful array order.
- Return the same comparison as structured JSON for agents and as an HTML view for humans. Both views refer to the same source manifests.
- Report which requirements and tests a change can affect. Mark unsupported or uncertain impact analysis explicitly. A diff identifies change; it does not prove causation or compliance.
- Conflicting edits to a requirement or evaluation rule require an explicit resolution record. Do not overwrite an existing revision or silently select a threshold.

The minimum demonstration shall change a parameter value, a unit, a requirement limit and an edge revision. It shall also add and remove a record. The comparison shall show each change. A repeated comparison shall be deterministic. Compare against the retained baseline without modifying it.

## Current implementation and remaining work

**Available in One-Piece:** immutable record revisions, atomic imports, reference and artifact checks, Git-managed canonical JSON, shared context/HTML data, and a limited HTML design-parameter comparison. `onepiece check` validates record integrity and evidence claim scope. It does not run simulations or prove compliance with every engineering requirement. The SysML API publishes the documented read profile; the standard `diffCommits` operation is not implemented.

**Available in Engineering Agents:** the balancing-cube adapter runs bounded CPU tests, supports GPU checks when available, and evaluates recorded numerical screening rules. Its results identify development test cases. It is a scenario-specific implementation, not a general requirement-verification scheduler.

**Remaining:** a generic verification-plan/execution contract; result-to-requirement coverage and applicability checks; a semantic configuration-diff API/CLI; shared JSON/HTML diff views; and change-driven re-execution. Branch/merge conflict handling and the SysML `diffCommits` service need separate implementation and tests. These items are not completed by restoring the competitor study.

The next MVP should connect these two capabilities for the existing Cube adapter. Keep the design-variable allowlist, fixed control period, fixed time step and CPU/GPU policy. Do not add half-step checks. Demonstrate change → diff → affected case → execution or justified re-evaluation → evidence → updated coverage before expanding the set of tools.
