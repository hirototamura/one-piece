# v0.3.0: reviewed Cube requirements and allocations

Human review on 2026-10-19 accepted the existing requirement statements and the proposed function/component allocation split. The review was recorded from the user's instruction and their scope confirmation, “Requirements and allocation split.”

- Active model and snapshot: `reviewed-20261019-1`.
- 22 obligations and 7 organizational groups: `status: reviewed`, `approval_state: human_reviewed`.
- 8 functions and 10 components: 5 functions and 7 components onboard; 3 functions and 3 tools in the external verification context.
- All 22 requirement assignments and 37 parameter assignments follow the accepted split. Requirements allocate to functions or products; functions allocate to implementing products. Mission and total budget retain whole-system responsibility.
- Review decision: `cube.review.requirements-allocation@reviewed-20261019-1`.
- Baseline: `cube.baseline.requirements-allocation@reviewed-20261019-1`; its 112 members include the archived proposal, human decision, requirements, functions, components, parameters, planned cases, snapshot and active model. Member SHA-256 values detect changes after review.

This release appends 113 canonical records. It preserves the earlier draft records, requirement meaning, parameter values and uncertainties, frozen dynamics, controller and evaluation contract. Snapshot context pins the exact reviewed function and component revisions.

## Verification scope

All 22 reviewed verification cases remain planned and `not_run`, with no evidence attached. Physical verification is not established. Open numerical limits and procedures remain unresolved. Existing design satisfaction declarations and numerical results retain their original revision targets; this release does not carry them forward automatically or adopt a hardware design.

Repository tests check record integrity, deterministic regeneration, accepted allocations, baseline hashes, exact context selection, and unchanged evidence states. They do not execute the Cube verification plans.

## Reproduce

From the source checkout, install the package, then run:

```sh
python projects/balancing-cube/review_requirements.py --write-docs
python -m pytest
```

The first command is idempotent against this release: it reports 113 unchanged records. Versioned JSON is authoritative; bilingual Markdown and SQLite indexes are derived views.

The release metadata asset contains the 113 appended records and their manifest. It depends on historical records in the tagged source checkout and contains no simulation artifact objects. Restore historical evidence objects from the existing evidence releases when an artifact audit is needed.

[Reviewed requirement text](balancing_cube_requirements.md) · [System model](system_model.md) · [Japanese release notes](../ja/reviewed_cube_release.md)
