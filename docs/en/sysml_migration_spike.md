# Cube SysML migration experiment

This bounded experiment explores a native SysML representation of a real reviewed Cube slice. One-Piece's versioned JSON remains authoritative. The example is a manually constructed candidate, not a production exporter, independent SysML certification, or a claim of complete SysML semantics.

## Pinned input and recovery

The source is commit `a9ba4933a54b413437f8487b847f8ff4e7e26c79292cc3ce79457307197ac6dd`, with record revision `reviewed-20261019-1`. The five records are `R-HOLD`, `cube.function.control-balance`, `cube.component.controller`, `D-SIDE`, and `cube.verify.R-HOLD`. Their canonical JSON bytes and SHA-256 digests are pinned in [spike.py](../../projects/balancing-cube/sysml_migration/spike.py). Canonical bytes are the One-Piece canonical serialization, not the original whitespace of the enclosing commit file.

Build a portable recovery package and check it without the original store:

```sh
python projects/balancing-cube/sysml_migration/spike.py --build /tmp/cube-hold-package.json
python projects/balancing-cube/sysml_migration/spike.py --check /tmp/cube-hold-package.json
python -m pytest -q tests/test_sysml_migration.py
```

The package stores the complete canonical bytes of each selected record and the native model as base64. The checker compares them with the pinned digests and identities. It detects changes but does not authenticate the publisher. It preserves all record fields, including unknown fields and references to records outside this slice; it does not bundle the full graph or artifact bytes. The selected verification case is a plan with `execution_status: not_run`, not a result or physical test evidence. Its references remain as recorded. No evidence object or hardware verification is invented.

## Mapping and open questions

The [native example](../../projects/balancing-cube/sysml_migration/hold.sysml) retains the `R-HOLD` English statement in a requirement and represents `cube.component.controller` as a part. `D-SIDE` is an attribute with `0.18[SI::m]`; it is a Cube side-length parameter, not a controller property. The reviewed control-balance function is tentatively represented as an action. Its nature and ownership require domain review before treating this as a general mapping.

Two named dependencies retain the direction of the selected requirement-to-function and function-to-controller links. Their names and endpoints provide traceability, but generic dependencies do not implement native allocation semantics. The requirement also has other allocations and constraints outside this example; the complete original links remain in its recovered record. Mapping of allocation, derive, constrain, satisfaction and verification to native constructs remains unresolved. No native satisfaction or verification assertion is made.

The source requirement is `human_reviewed` and its verification is `not_run`. The native statement alone does not encode those states, its complete conditions, physical evidence scope, provenance, Japanese translation or historical revision references. Those fields are preserved in the recovery package, not asserted by the native model. A model importer must not interpret review as verification or infer proof from an allocation.

## Independent validation

On 2026-11-01, OpenMBEE OpenSysML `v0.11.0` (commit `ddf4df00037d6ddbfb1fa9d743a4389f75c9e2dc`) accepted the example with `sysml -validate -strict`. The macOS arm64 release asset `sysml-darwin-arm64.tar.gz` had SHA-256 `9bff5c4195062b5e2cbf9ca69360f64569d03b0b5ff1c7e91c872cdec00efceb`, matching the [published release](https://github.com/Open-MBEE/OpenSysML/releases/tag/v0.11.0). Re-run with that tool using:

```sh
sysml -validate -strict projects/balancing-cube/sysml_migration/hold.sysml
sysml -convert api-json -o /tmp/cube-hold-api.json projects/balancing-cube/sysml_migration/hold.sysml
```

In the experimental API JSON conversion, the tool identifies `hold` as `RequirementUsage`, `controller` as `PartUsage`, `balanceControl` as `ActionUsage`, and `cubeSide` as `AttributeUsage`. It reports both named dependencies with the intended source and target. OpenSysML marks that conversion experimental; this inspection is not a tool-to-tool interchange test.

This is one tool's validation of one example. No external-tool round trip or general-purpose SysML importer has been demonstrated. Verification of recovery bytes is separate from validation of the candidate native semantics.
