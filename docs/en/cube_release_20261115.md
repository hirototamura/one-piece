# v0.5.0 release candidate: reviewed Cube and Explorer

Prepared on 2026-11-15 (Asia/Tokyo). Candidate status; tag and release publication remain pending.

The reviewed model and snapshot are both `requirements-review-20261115-3`.
The release index is `projects/balancing-cube/release_candidate.json`, which pins
SHA-256 identities for the active model, snapshot, review decision, baseline,
CM-01 and configuration catalogue. The baseline has 117 hashed members.
Historical records and the v0.3.0 release notes remain unchanged.

The model contains 19 requirements, 7 classification groups, 3 separate constraints,
37 KDPs, 9 functions and 10 components. It requires balancing on all eight corners,
a shared 10 s demonstration interval, and automatic corner identification before
balance control starts. Material selection is a design choice; budget is a project
constraint; part printing limits and Japanese procurement are manufacturing constraints.
Yaw is about the fixed vertical axis at balance start. R-TRACE belongs to configuration
management. System performance, supporting drive requirements and measurement requirements
have explicit derivation links.

The packaged Systems Requirements Explorer retains the current published UI, font sizes,
removed panels, bilingual text, KDP navigation and local review/export workflow.
It runs without Sites or Node.js; bundled ECLSS/scrubber examples are scenario contracts.

## Candidate validation and reproduction

```sh
python -m pip install -e .
python projects/balancing-cube/apply_requirement_review.py --write-docs
python -m pytest
onepiece --store projects/balancing-cube/store explorer serve \
  --model-revision requirements-review-20261115-3
```

Regeneration reports 118 unchanged records. Test the installed wheel separately
from the source tree before tagging. Release preparation includes wheel, source archive,
portable Explorer and SHA-256 checksums; generated artifacts stay outside Git.
Merge the stacked parent PR and this candidate PR, then rebuild from the final release
commit before creating `v0.5.0` and publishing its matching assets.

## Engineering limits retained

All 22 verification plans (19 requirements and 3 constraints) remain `not_run` with
no evidence attached. The exact unresolved items are included in the release index.
The proposed horizontal roll/pitch axes still require review. Hardware limits and
measurement procedures retain unresolved items. The controller edit policy is recorded;
algorithm proposal/execution and automatic corner detection are not implemented.
Numerical scoring is unchanged, historical evidence retains its original applicability,
and this release does not adopt a hardware design or establish physical verification.
