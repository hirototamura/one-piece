# One Piece Engineering

A local, versioned system model and engineering evidence core. Requirements, Key Design Parameters (KDPs), detailed model parameters, designs, experiments and decisions share stable IDs and explicit revision references. Humans and Engineering Agents consume the same records.

The graph is **inspired by SysML v2**. This project does not implement the SysML language or claim standard API conformance. Simulation evidence and CPU/GPU numerical agreement do not establish physical-world validation.

[理念 / Philosophy](docs/ja/CORE.md) · [System model](docs/en/SYSTEM_MODEL.md) · [システムモデル](docs/ja/SYSTEM_MODEL.md) · [Development history](docs/en/DEVELOPMENT_PROGRESS.md)

## Install and run

Python 3.11 or newer. The runtime uses the standard library; no database server is required.

```sh
python -m pip install -e '.[test]'
onepiece --help
python -m pytest
```

The following examples use `.onepiece` as the local store. Put `--store PATH` before the subcommand to select another store.

```sh
onepiece --store .onepiece import records.json --artifacts-root ./source-results
onepiece --store .onepiece check
onepiece --store .onepiece context --project balancing-cube --max-designs 20 --max-evidence 50 --output context.json
onepiece --store .onepiece report report.html --project balancing-cube
onepiece --store .onepiece bundle evidence.zip --project balancing-cube
```

`bundle` prints the ZIP SHA-256. Imports and downloads of ZIP evidence require the expected hash obtained from the publisher:

```sh
onepiece --store restored import evidence.zip --sha256 EXPECTED_SHA256
onepiece --store restored fetch https://example.org/releases/evidence.zip --sha256 EXPECTED_SHA256
onepiece --store restored reindex
onepiece --store restored check
```

`fetch` also accepts a local `file:///absolute/path/evidence.zip` URL for offline restoration. HTTPS downloads are bounded; redirects, ZIP entries, expansion limits, artifact hashes and references are checked before publication. ZIP contents are not extracted to caller-controlled paths. A published Release asset is a distribution of evidence, not approval of a requirement or design.

## What is authoritative

A store contains atomic immutable JSON commits:

```text
STORE/
  commits/<commit-sha256>/
    records.json       # canonical versioned envelopes
    manifest.json      # record count and canonical digest
    objects/<sha256>   # evidence bytes; excluded from Git
  index.sqlite         # disposable, rebuildable query index
```

An import is validated as a complete batch. Invalid references, changed content for an existing ID/revision, artifact traversal, missing bytes or digest mismatches reject the batch. An atomic directory rename publishes all new records together. Re-importing identical records is idempotent. Records never silently overwrite an existing revision. SQLite can be deleted and reconstructed from the JSON commits, and its contents cannot replace canonical record bodies.

Compact canonical JSON under `projects/*/store/commits/` can be versioned in Git. Artifact objects, locks, temporary stages and SQLite files are ignored. **A metadata-only Git clone does not contain the original evidence bytes.** Graph/context queries can still read records; `check` and `bundle` report missing artifacts until the hash-checked evidence bundle has been restored. An absent artifact is never treated as a verification pass.

## Record and graph contract

The public structural contract is [schemas/record.schema.json](schemas/record.schema.json), also included in the installed package as `onepiece.record_schema()`. Cross-record graph, artifact-integrity and evidence-scope checks are additional semantic checks. Unknown envelope/data extension fields are preserved; the schema version remains explicit.

```python
from onepiece import Store, make_record, ref

mission = make_record(
    project_id="cube", id="REQ-MISSION", kind="requirement",
    actor={"type": "human", "id": "engineer"},
    data={"level": "mission", "text": "Demonstrate controlled vertex balance",
          "approval_state": "draft", "success_criteria": {"method": "integrated_test"}},
)
system = make_record(
    project_id="cube", id="REQ-SYSTEM", kind="requirement",
    data={"level": "system", "approval_state": "draft",
          "success_criteria": {"tilt_limit": 5, "unit": "deg"}},
    links=[{"type": "derive", "target": ref(mission)}],
)
store = Store(".onepiece")
store.import_records([mission, system])
context = store.context("cube", max_designs=20, max_evidence=50)
```

Every envelope contains `schema_version`, `project_id`, `id`, `revision`, `kind`, `product_node`, `created_at`, `actor`, `data`, `links`, and `artifacts`. Each artifact has a safe relative logical `path` and SHA-256; `size_bytes` and origin `uri` are optional. Import copies and verifies bytes from `artifacts_root`. A URI alone does not substitute for evidence bytes.

Edges pin a target ID and revision in the same project:

- `derive`: child requirement → parent requirement, or same-kind design/policy/iteration ancestry. Cycles are rejected.
- `satisfy`: design/product → intended requirement. This is a correspondence declaration, not proof of compliance.
- `verify`: evidence/verification/evaluation → requirement or test case. The evidence carries outcome, conditions, fidelity and applicability.
- `allocate`: requirement/function/KDP/parameter → responsible product.
- `constrain`: requirement/specification/constraint → parameter/design/product/model.

System requirements branch to **both operational and subsystem requirements**. Product/module ownership and model-parameter bindings remain explicit. A simulation snapshot preserves the model, controller, evaluation contract and parameter bindings used for a run. Historical imports retain their source approval states and uncertainties; they do not baseline newly drafted requirements.

## Agent context and authority

`Store.context(project_id, product_node=None, kinds=None, max_designs=20, max_evidence=50)` retains requirement/KDP units, uncertainty and source semantics. An explicit system-model `simulation_snapshot_ref` selects the current context by default; an optional exact `snapshot_ref` overrides it. Snapshot `context_refs` pin requirement and KDP revisions. Canonical history remains queryable through `records()` and is never rewritten.

The comparison design and campaign summary are mandatory **outside** design/evidence count and kind filters. Balancing Cube returns five optional designs plus its comparison design, eight evidence records and the prior-46 summary. Omitted edge references and references embedded in data are enumerated. The CLI exposes `--snapshot-id` and `--snapshot-revision`; HTML exports the same selected context. Real-provider context-window capacity has not been tested.

Development iterations may propose design changes, run bounded experiments and record decisions under their configured authority. Requirements/evaluation-contract adoption is separate from automatic experiment decisions. Imported historical `baseline` labels are not approval of a new design.

A baseline is an explicit **human configuration-identity action** with pinned member revisions and hashes:

```sh
onepiece --store .onepiece baseline --project cube --id BASE-001 --human-actor engineer --reason 'Reviewed configuration and stated evidence limits'
```

This local CLI records the declared actor; it is not an identity-authentication service. Agents must not invoke the human operation for automatic loop decisions. Baselines do not imply hardware acceptance. A record claiming physical verification needs explicit physical-test evidence and artifact bytes; numerical or missing evidence cannot make that claim.

## Engineering integration

The [system model](docs/en/SYSTEM_MODEL.md) describes the minimal structure and semantics. Integration adapters and project records can be added without changing the generic envelope. The balancing-cube adapter preserves original GPU/CPU evidence, historical supplemental CPU time-step evidence, and later CPU replays as distinct sources. A six-second numerical experiment does not verify a thirty-second hardware requirement.

The standalone HTML report is a projection of canonical records. The runtime execution platform, engineering-agent task state and immutable evidence record have separate responsibilities; there is no second authoritative requirement or KDP copy inside the agent prompt.

Licensed under [Apache-2.0](LICENSE).
