# Balancing Cube: system model and numerical evidence

One-Piece owns the versioned system model. Engineering Agents reads it, proposes bounded changes, runs MuJoCo, and records results before the next proposal. Canonical JSON commits under `store/commits/` are tracked in Git; the SQLite index, artifact objects and generated HTML are rebuildable local files.

The imported historical record contains 16 original requirements plus 5 explicitly drafted hierarchy nodes, 37 KDPs, 60 numerical model leaves, 2,048 designs, and distinct original GPU/CPU, supplemental CPU and replay evidence. The prior 46 candidates retain **31 pass / 9 fail / 6 inconclusive**. `D-000544-52890@legacy-20261009` is the existing paired numerical comparison reference. No adopted human baseline has been created.

The original `cube.simulation.snapshot@legacy-20261009` stays immutable. New runs use `cube.simulation.snapshot@fixed-dt-mvp-1`, which pins the comparison design, retains the nominal controller-design plant and saved K, and applies fixed-timestep CPU/GPU checks. Historical half-step evidence remains history; this pipeline does not run new half-step checks. Original KDP registry values and resolved model values remain distinct where they differ.

## Restore and inspect

Install One-Piece 0.1.0 from this checkout or the wheel attached to the [evidence Release](https://github.com/hirototamura/one-piece/releases/tag/evidence-balancing-cube-20261010). [evidence-manifest.json](evidence-manifest.json) pins asset URLs, sizes and SHA-256 values. A Git clone includes metadata only: restore artifacts before `check` or execution.

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

The Fake LLM proposals did not improve the numerical reference. CPU-only proposals remain provisional. New GPU execution, real LLM improvement, hardware measurements and physical validation have not been performed. Six-second numerical results do not verify the draft thirty-second hardware holding requirement. Existing unstructured acceptance criteria remain explicit warnings; imported historical states do not approve the new hierarchy.

The system graph uses `derive / satisfy / verify / allocate / constrain`; `satisfy` records intent and `verify` carries scoped evidence. The [system-model guide](../../docs/ja/SYSTEM_MODEL.md) explains the NASA/SpaceX principles, and the [Engineering Agents guide](https://github.com/hirototamura/engineering_agents/blob/codex/mujoco-evidence-loop/docs/ja/mujoco-one-piece.md) describes the bounded ENPIRE-inspired pipeline. It evolves hypothesis, priority KDPs and search step, with hardware/software changes limited to the approved MVP variables.
