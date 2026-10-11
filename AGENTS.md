# One-Piece engineering record core

These instructions apply to every agent and human contributor, independent of tool or provider. Read [Engineering standards](docs/engineering/standards.md), [CORE](docs/en/CORE.md), [system model](docs/en/SYSTEM_MODEL.md), [NASA SE](docs/engineering/nasa-se.md), and [SpaceX-style SE](docs/engineering/spacex-se.md) before engineering changes. All entry points refer to these shared guides.

Use **ISO/IEC/IEEE 29148:2018 as the first source of requirements standards**. Apply **ASD-STE100 Simplified Technical English where applicable** to English requirements and technical documents. Preserve technical meaning and source approval state. Record unavailable normative text or unresolved clauses; do not invent compliance claims.

Versioned JSON is the source of truth; the SQLite index is disposable. Keep the system graph minimal and traceable. Preserve requirements, KDPs, detailed parameters, evidence provenance and human decisions. Relations are derive/satisfy/verify/allocate/constrain. The [OMG Systems Modeling API boundary](docs/en/SYSML_API.md) uses standard payloads and operations within its documented scope. Do not claim full SysML language or full API service coverage.

Agents draft and run bounded development experiments. Humans establish requirements, evaluation contracts and adopted baselines. A numerical simulation result does not demonstrate physical-world validity.

Run `python -m pytest` before submitting changes. Keep artifact objects, indexes, generated reports and virtual environments out of Git; publish content-addressed evidence bundles as Release assets.
