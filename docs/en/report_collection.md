# Report collection and recorded design campaigns

One-Piece owns the canonical requirements, parameters, configurations, evidence
and judgments. Engineering Agents owns the derived bilingual report collection,
page-preview capture and translation tools. The report collection is not another
source of engineering truth.

The [Engineering Agents report-library guide](https://github.com/hirototamura/engineering_agents/blob/codex/mujoco-evidence-loop/docs/en/report_library.md)
describes the local catalog, latest-title grouping, language links and actual
page screenshots. The main view selects the newest source-file modification time
for a matching title. This rule does not replace canonical record revisions or
the model diff. All original source versions remain available.

## Recorded Qwen development campaigns

The project evidence index identifies three real-LLM campaigns: one interrupted
attempt, a completed ten-iteration run, and a completed twenty-iteration run.
The selected canonical record families contain 122 records. Local acceptance
and Fake LLM runs are retained as verification artifacts and are not added to
the canonical store by this publication.

The ten-iteration run has best exploration score `0.9906165004570363`.
Its independent twelve-case check has score `0.9065363695185216`, with eleven
screening passes and CPU/GPU numerical agreement. The twenty-iteration run has
best exploration score `0.9914337403352801`. Its independent check has score
`0.8833405346349856`, eleven screening passes, and `numeric_gpu_verified: false`.
These are different evidence roles; the higher exploration score does not
establish a better independently verified design.

Both selections remain provisional. No human-adopted baseline is created.
Six-second numerical trials do not demonstrate thirty-second hardware holding,
physical fidelity or calibrated sensor behavior. The interrupted attempt keeps
its incomplete status and failure reason.

## Durable evidence

Compact immutable record JSON and retrieval indexes belong in Git. Generated
HTML, translations, thumbnails, trajectories, LLM request traces and test logs
belong in hash-pinned Release assets. Request traces retain fitted prompts and
final responses without credentials or private reasoning text. A Release does
not approve requirements or adopt a design.

The project index records the source snapshots, exact run IDs, asset locations,
SHA-256 values and verification limits. The CLI `context` remains the agent
interface. The HTML collection serves human readers.
