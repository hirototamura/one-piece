# Requirements explorer

One-Piece owns the requirements explorer source and its data projection. The
original local prototype was migrated from commit
`d5bcc0c70be1f7b190fbe8368c90e5eec4ac75bf`. The maintained assets are packaged
under `src/onepiece/explorer_assets/`. Generated pages and model data stay out of Git.

Build the reviewed Cube view from the source checkout:

```sh
python -m pip install -e .
onepiece --store projects/balancing-cube/store explorer build \
  projects/balancing-cube/explorer --model-revision reviewed-20261019-1
python -m http.server 8791 --bind 127.0.0.1 \
  --directory projects/balancing-cube/explorer
```

Open `http://127.0.0.1:8791/`. Stop the local static server with Ctrl-C. This
serves only the generated directory. It does not expose a writable store or start
a model API. The installed wheel includes the assets; Node.js is not required.

The reviewed projection contains 22 obligations, 7 groups, 37 linked parameters
and 22 planned verification cases. These counts come from the selected snapshot.
The builder checks canonical JSON through `Store`, selects one project, and
resolves exact ID/revision references. `--model-id` and `--model-revision` select
a specific system model. If the revision is omitted, the latest source model
for that ID is selected; its recorded approval state is displayed without promotion.

The source model and snapshot hashes, record-set hash, build inputs and output
file hashes are saved in `provenance.json` and `explorer-manifest.json`. Displayed
English and Japanese requirement text comes from the same source records. Draft
architecture overlays apply only to their exact base-model revision. A design's
`satisfy` links remain intent declarations tied to their original requirement
revisions. They do not become verification results or carry forward automatically.

Browser edits are local proposals. Local storage is scoped to the project and
model digest. Exported review packets include the exact model and snapshot
references. The explorer cannot approve requirements, import records or change
a baseline. Human decisions still enter the versioned record workflow.

The graph presents the existing One-Piece record relationships. Use
[`onepiece sysml`](sysml_api.md) for the documented OMG Systems Modeling API
boundary. The explorer is not an additional SysML language implementation.

ECLSS and scrubber comparison panels are optional. To include the explicitly
selected Engineering Agents scenario files, install `.[explorer]` and pass
`--engineering-agents-root /path/to/engineering_agents`. Their source hashes are
recorded. These scenario contracts are not reviewed One-Piece requirements.

[System model](system_model.md) · [Dataset retrieval](dataset_storage.md)
