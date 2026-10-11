# One-Piece engineering record core

These instructions apply to every agent and human contributor, independent of tool or provider. Read [Engineering standards](docs/engineering/standards.md), [CORE](docs/en/CORE.md), [strategy](docs/en/strategy.md), [system model](docs/en/system_model.md), [NASA SE](docs/engineering/nasa_se.md), and [SpaceX-style SE](docs/engineering/spacex_se.md) before engineering changes. All entry points refer to these shared guides.

## Protected philosophy and document names

- `docs/**/CORE.md` holds long-term philosophy and vision. Agents shall normally leave it unchanged. **Obtain explicit human approval for the specific proposed edit before editing any CORE.md.** This includes formatting, translation and link changes. A feature request, general documentation task, or an agent-generated plan is not approval to edit CORE.md. An explicit human instruction that specifies a CORE edit authorizes that edit only. No agent authority mode waives this rule.
- Prepare proposals outside CORE.md until approved. Put concrete strategy, specification decisions and current implementation priorities in [strategy.md](docs/en/strategy.md) / [日本語](docs/ja/strategy.md). Link supporting technical documents from strategy.md.
- Every Markdown filename under `docs/`, except `CORE.md`, shall use lowercase snake_case, for example `system_model.md` or `nasa_se.md`. Preserve `CORE.md` as the sole uppercase exception. Update references when a document moves.

## Engineering record contract

Use **ISO/IEC/IEEE 29148:2018 as the first source of requirements standards**. Apply **ASD-STE100 Simplified Technical English where applicable** to English requirements and technical documents. Preserve technical meaning and source approval state. Record unavailable normative text or unresolved clauses; do not invent compliance claims.

Versioned JSON is the source of truth; the SQLite index is disposable. Keep the system graph minimal and traceable. Preserve requirements, KDPs, detailed parameters, evidence provenance and human decisions. Relations are derive/satisfy/verify/allocate/constrain. The [OMG Systems Modeling API boundary](docs/en/sysml_api.md) uses standard payloads and operations within its documented scope. Do not claim full SysML language or full API service coverage.

Agents draft and run bounded development experiments. Humans establish requirements, evaluation contracts and adopted baselines. A numerical simulation result does not demonstrate physical-world validity.

Run `python -m pytest` before submitting changes. Keep artifact objects, indexes, generated reports and virtual environments out of Git; publish content-addressed evidence bundles as Release assets.
