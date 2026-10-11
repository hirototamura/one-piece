# Balancing Cube: system model and numerical evidence

One-Piece owns the versioned system model. Engineering Agents reads it, proposes bounded changes, runs MuJoCo, and records results before the next proposal. Canonical JSON commits under `store/commits/` are tracked in Git; the SQLite index, artifact objects and generated HTML are rebuildable local files.

The imported historical record contains 16 original requirements plus 5 explicitly drafted hierarchy nodes, 37 KDPs, 60 numerical model leaves, 2,048 designs, and distinct original GPU/CPU, supplemental CPU and replay evidence. The prior 46 candidates retain **31 pass / 9 fail / 6 inconclusive**. `D-000544-52890@legacy-20261009` is the existing paired numerical comparison reference. No adopted human baseline has been created.

The original `cube.simulation.snapshot@legacy-20261009` stays immutable. New runs use `cube.simulation.snapshot@fixed-dt-mvp-2`, which pins the comparison design, retains the nominal controller-design plant and saved K, and applies fixed-timestep CPU/GPU checks. Historical half-step evidence remains history; this pipeline does not run new half-step checks. Original KDP registry values and resolved model values remain distinct where they differ.

## Standards and language revision

The current One-Piece context and report use `cube.simulation.snapshot@standards-draft-20261011-2`. The first standards draft added 96 immutable records to the 6,620 historical records. The shall-priority correction adds 91 records, including current revisions of 37 KDPs and their exact requirement links. It preserves the first draft and makes 6,807 canonical records. The 22 test obligations and 7 organizational containers have English source text and aligned Japanese translations. Eight atomic child requirements replace the compound manufacturing and drive obligations. The original IDs remain traceable. All revised wording needs human review; original source states are retained separately.

[English requirement view](../../docs/en/balancing_cube_requirements.md) / [日本語訳](../../docs/ja/balancing_cube_requirements.md) are generated from the canonical records. [The shared writing policy](../../docs/engineering/standards.md) identifies the source priority: ISO/IEC/IEEE 29148:2018, NASA standards and requirements guidance, then compatible ASD-STE100 Issue 9 rules. English requirements use `shall` under NASA requirements guidance. Its full normative text was not available, so a clause audit is still necessary. A complete STE dictionary audit is also not performed.

```sh
PYTHONPATH=src python projects/balancing-cube/migrate_standards.py --write-docs
PYTHONPATH=src python -m onepiece --store projects/balancing-cube/store report projects/balancing-cube/report/index.html --project balancing-cube
```

The first command is idempotent. The authoring script and language catalogs are migration inputs; the Store is the source of truth. The 22 verification cases are plans with no result evidence. Numerical test conditions, physics, saved K, evaluation rules, parameter values and historical evidence targets are unchanged. The API keeps the existing `onepiece-annotation-graph-1` profile and exact source revisions.

Engineering Agents keeps its explicit `fixed-dt-mvp-2` execution default. For inspection of the revised draft, construct `MechanicalBridge(..., snapshot_revision="standards-draft-20261011-2")`. This selects the new requirement text and the same numerical configuration; it does not approve the requirements or verify them with old results.

## Restore and inspect

Install One-Piece 0.1.1 from this checkout or the wheel attached to the [evidence Release](https://github.com/hirototamura/one-piece/releases/tag/evidence-balancing-cube-20261011-review2). [evidence-manifest.json](evidence-manifest.json) pins asset URLs, sizes and SHA-256 values. A Git clone includes metadata only: restore artifacts before `check` or execution.

```sh
python -m pip install -e .
python - <<'PY'
import json
from onepiece import Store
m = json.load(open('projects/balancing-cube/evidence-manifest.json'))
print(Store('projects/balancing-cube/store').fetch(
    m['bundle']['url'], expected_sha256=m['bundle']['sha256']))
PY
onepiece --store projects/balancing-cube/store check --project balancing-cube
onepiece --store projects/balancing-cube/store report projects/balancing-cube/report/index.html --project balancing-cube
```

For offline use, download the evidence ZIP on a connected machine, transfer it, then run `onepiece --store projects/balancing-cube/store import /path/to/evidence.zip --sha256 HASH_FROM_MANIFEST`. Identical metadata is retained while missing objects are restored. Repeated delivery creates no duplicate records. The separate report ZIP opens directly at `index.html` and includes its linked original evidence; JSON/context and the CLI remain the agent interface.

## Acceptance and limits

The final offline acceptance is `cube.acceptance.offline-20261010@2`. It records the code revision, test outputs, four saved-K CPU reproductions, two Fake LLM rounds with actual CPU physics, round-two retrieval of persisted feedback, evolved search-policy data, and unchanged original hashes. ECLSS remains independently tested through its existing two-run workflow. The evidence index also records metadata-only clone restoration, canonical JSON preservation and duplicate-delivery checks.

The Fake LLM proposals did not improve the numerical reference. CPU-only proposals remain provisional. New GPU execution, real LLM improvement, hardware measurements and physical validation have not been performed. Six-second numerical results do not verify the draft thirty-second hardware holding requirement. Unstructured acceptance criteria in historical revisions remain explicit warnings; imported historical states do not approve the new hierarchy.

The system graph uses `derive / satisfy / verify / allocate / constrain`; `satisfy` records intent and `verify` carries scoped evidence. The [system-model guide](../../docs/ja/system_model.md) explains the NASA/SpaceX principles, and the [Engineering Agents guide](https://github.com/hirototamura/engineering_agents/blob/codex/mujoco-evidence-loop/docs/ja/mujoco-one-piece.md) describes the bounded ENPIRE-inspired pipeline. It evolves hypothesis, priority KDPs and suggested search step (advisory), with hardware/software changes limited to the approved MVP variables.

## Trace corrections and acceptance isolation

`fixed-dt-mvp-2` superseded v1 before the standards draft. It remains the Engineering Agents execution default. Only trace metadata changed in that revision: M-VERTEX allocates to cube.system; numerical evaluations verify the six-second development test cases instead of the hardware mission. Historical requirement `status` describes the source statement, not a verification outcome. The standards draft uses `status: draft` and retains that earlier state as `source_status`. `hardware_verification_required` identifies work still to demonstrate with hardware; it is not a pass flag. `physical_verified` remains null. Physics, controller K, conditions and outcomes are unchanged.

The 4,445 previously published records remain immutable history, including earlier offline acceptance runs. The 2,175 appended revisions bring canonical history to 6,620 records; current projections contain one revision per ID. The exact comparison design and campaign_summary are outside context count limits, so acceptance candidates cannot hide the best original design or 31/9/6 summary. New acceptance runs use a separate temporary store; their logs are published in the new Release verification ZIP. The original 0.1.0 Release remains an archive, not the current install target.

CI builds and tests the installed 0.1.1 wheel on Python 3.11/3.12. Engineering Agents uses that Release wheel with its SHA-256 pin and makes MuJoCo CPU integration tests mandatory with zero dependency skips. Requested-but-unavailable GPU execution is inconclusive and has a nonzero process exit; no GPU or physical result is inferred.
