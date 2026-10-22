# Balancing Cube: system model and numerical evidence

One-Piece owns the versioned system model. Engineering Agents reads it, proposes bounded changes, runs MuJoCo, and records results before the next proposal. Canonical JSON commits under `store/commits/` are tracked in Git; the SQLite index, artifact objects and generated HTML are rebuildable local files.

## Current configuration roles, 21 October 2026

Use the [configuration catalogue and BOM assessment](../../docs/en/cube_configuration_catalogue.md). CM-01 is the reviewed requirements view, CM-02 is the lower-face runnable default, CM-03 is historical multi-agent evidence, and CM-04 is the new fixed BOM reference. They are separate roles with exact revisions. The BOM assessment ran 34 simulations and no design iterations. The sections below retain the earlier migration/release history; their old defaults are not current selections.

The imported historical record contains 16 original requirements plus 5 explicitly drafted hierarchy nodes, 37 KDPs, 60 numerical model leaves, 2,048 designs, and distinct original GPU/CPU, supplemental CPU and replay evidence. The prior 46 candidates retain **31 pass / 9 fail / 6 inconclusive**. `D-000544-52890@legacy-20261009` is the existing paired numerical comparison reference. No adopted human baseline has been created.

The original `cube.simulation.snapshot@legacy-20261009` stays immutable. The earlier campaign used `cube.simulation.snapshot@fixed-dt-mvp-2`, which pins the comparison design, retains the nominal controller-design plant and saved K, and applies fixed-timestep implementation checks. Historical half-step evidence remains history. Original KDP registry values and resolved model values remain distinct where they differ.

## Historical standards and language revision, 11 October 2026

At this checkpoint, the One-Piece context and report used `cube.simulation.snapshot@standards-draft-20261011-2`. The first standards draft added 96 immutable records to the 6,620 historical records. The shall-priority correction added 91 records, including 37 KDP revisions and their exact requirement links. It preserved the first draft and made 6,807 canonical records. The 22 test obligations and 7 organizational containers had English source text and aligned Japanese translations. Eight atomic child requirements replaced the compound manufacturing and drive obligations. The original IDs remain traceable. This wording was reviewed on 19 October; the reviewed revision is now CM-01.

[English requirement view](../../docs/en/balancing_cube_requirements.md) / [日本語訳](../../docs/ja/balancing_cube_requirements.md) are generated from the canonical records. [The shared writing policy](../../docs/engineering/standards.md) identifies the source priority: ISO/IEC/IEEE 29148:2018, NASA standards and requirements guidance, then compatible ASD-STE100 Issue 9 rules. English requirements use `shall` under NASA requirements guidance. Its full normative text was not available, so a clause audit is still necessary. A complete STE dictionary audit is also not performed.

```sh
PYTHONPATH=src python projects/balancing-cube/migrate_standards.py --write-docs
PYTHONPATH=src python -m onepiece --store projects/balancing-cube/store report projects/balancing-cube/report/index.html --project balancing-cube
```

The first command is idempotent. The authoring script and language catalogs are migration inputs; the Store is the source of truth. The 22 verification cases are plans with no result evidence. Numerical test conditions, physics, saved K, evaluation rules, parameter values and historical evidence targets are unchanged. The API keeps the existing `onepiece-annotation-graph-1` profile and exact source revisions.

Engineering Agents used `fixed-dt-mvp-2` as its execution default at this checkpoint. To inspect that historical draft, construct `MechanicalBridge(..., snapshot_revision="standards-draft-20261011-2")`. The exact revision selects its requirement text and numerical configuration; old evidence does not verify later requirements.

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

The Fake LLM proposals did not improve the numerical reference. CPU-only proposals remain provisional. At that offline acceptance checkpoint, new GPU execution and real LLM improvement had not been performed. The later Qwen campaigns below add numerical CPU/GPU execution evidence. Hardware measurements and physical validation remain unperformed. Six-second numerical results do not verify the draft thirty-second hardware holding requirement. Unstructured acceptance criteria in historical revisions remain explicit warnings; imported historical states do not approve the new hierarchy.

The system graph uses `derive / satisfy / verify / allocate / constrain`; `satisfy` records intent and `verify` carries scoped evidence. The [system-model guide](../../docs/ja/system_model.md) explains the NASA/SpaceX principles, and the [Engineering Agents guide](https://github.com/hirototamura/engineering_agents/blob/codex/mujoco-evidence-loop/docs/ja/mujoco-one-piece.md) describes the bounded ENPIRE-inspired pipeline. It evolves hypothesis, priority KDPs and suggested search step (advisory), with hardware/software changes limited to the approved MVP variables.

## Trace corrections and acceptance isolation

`fixed-dt-mvp-2` superseded v1 before the standards draft. It was the Engineering Agents execution default for the earlier campaigns. Only trace metadata changed in that revision: M-VERTEX allocates to cube.system; numerical evaluations verify the six-second development test cases instead of the hardware mission. Historical requirement `status` describes the source statement, not a verification outcome. The standards draft uses `status: draft` and retains that earlier state as `source_status`. `hardware_verification_required` identifies work still to demonstrate with hardware; it is not a pass flag. `physical_verified` remains null. Physics, controller K, conditions and outcomes are unchanged.

The 4,445 previously published records remain immutable history, including earlier offline acceptance runs. The 2,175 appended revisions bring canonical history to 6,620 records; current projections contain one revision per ID. The exact comparison design and campaign_summary are outside context count limits, so acceptance candidates cannot hide the best original design or 31/9/6 summary. New acceptance runs use a separate temporary store; their logs are published in the new Release verification ZIP. The original 0.1.0 Release remains an archive, not the current install target.

CI builds and tests the installed 0.1.1 wheel on Python 3.11/3.12. Engineering Agents uses that Release wheel with its SHA-256 pin and makes MuJoCo CPU integration tests mandatory with zero dependency skips. Requested-but-unavailable GPU execution is inconclusive and has a nonzero process exit; no GPU or physical result is inferred.

## Qwen memory campaigns and bilingual collection

The [campaign evidence index](campaign-evidence-manifest.json) adds three real-LLM
run families (122 records) to the 6,807-record history: an interrupted attempt,
ten completed rounds, and twenty completed rounds. The published metadata has
6,929 records. Unpublished local acceptance/Fake LLM runs are excluded.
See [report collection and campaign limits](../../docs/en/report_collection.md).

The historical evidence index above remains unchanged. For this expanded Git
checkout, restore **all three** new packs before checking or running the store:

```sh
python - <<'PY'
import json
from onepiece import Store
m = json.load(open('projects/balancing-cube/campaign-evidence-manifest.json'))
s = Store('projects/balancing-cube/store')
for pack in m['packs']:
    print(s.fetch(pack['url'], expected_sha256=pack['sha256']))
assert s.check('balancing-cube')['ok']
PY
```

Each pack stays within the existing ZIP safety limits. References resolve against
the canonical JSON metadata from this checkout. The packs restore artifact bytes;
they do not replace Git metadata or change record revisions.
The export helper reproduces the selection and checks clone restoration and
idempotent import. The translated collection and screenshots are derived outputs
maintained by Engineering Agents, not canonical model data.

## Local first-trial correction, 17 October 2026

The 17 October local trial selected `cube.simulation.snapshot@bottom-corner-000-20261017-3`: wheel mounts on the three faces incident to corner 000, with the retained tested MASS controller. This remains CM-02, the runnable default; the reviewed requirements view is CM-01. The mission intent covers all eight corners; only corner 000 is implemented in this trial. Read the [English source](../../docs/en/bottom_corner_trial.md) or [Japanese translation](../../docs/ja/bottom_corner_trial.md). The local evidence and model revisions do not change earlier Release manifests. No physical baseline is adopted.
