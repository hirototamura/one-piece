# Shared engineering standards

This policy applies to humans and every agent, including Codex, Claude and Cursor. The canonical guides are [NASA SE](nasa_se.md) and [SpaceX-style SE](spacex_se.md). Tool-specific files are entry points, not separate policies.

Follow the [document-governance rules](../../AGENTS.md#protected-philosophy-and-document-names) before edits. CORE.md holds protected long-term philosophy. Current strategy and specification choices belong in [strategy.md](../en/strategy.md) / [日本語](../ja/strategy.md).

## Requirements: first source

Use **ISO/IEC/IEEE 29148:2018, Systems and software engineering — Life cycle processes — Requirements engineering**, as the first source for requirements engineering, requirement information items, and requirement quality. Use NASA and SpaceX-style guides for supporting engineering methods. Do not replace the requirements standard with a company handbook. Record the standard edition and applicable clause when the licensed text is available. The [ISO catalogue](https://www.iso.org/standard/72089.html) identifies the standard; it does not supply its full normative text. Do not invent clause numbers or claim full compliance from this policy or an automated check.

For each new or revised requirement, record its stable ID, revision, responsible product, source, rationale, approval state, parent trace, conditions, measurable acceptance criteria, units and verification method. State one obligation with a clear subject. Separate requirements from assumptions, design choices and results. Identify missing information as unresolved. Preserve historical source wording and status; propose corrections as new drafts. Humans approve requirements, evaluation contracts and adopted baselines.

## Technical English

Use **ASD-STE100 Simplified Technical English where applicable** in English requirements and technical documents. Use short sentences, active voice, consistent defined terms and explicit units. Keep one instruction or obligation per sentence. Avoid ambiguous pronouns and unnecessary synonyms. Keep normative `shall`, standard identifiers, equations, API names and defined technical terms when they are necessary for precision. Do not change a requirement's meaning to simplify its language. Japanese documents may retain Japanese text; keep an aligned English version when needed for exchange.

Consult the official [ASD-STE100 site](https://www.asd-ste100.org/) and [FAQ](https://www.asd-ste100.org/STE_faq.html) for the current issue and access to the rules and dictionary. The requested [STEMG page](https://asd-ste100.org/ASD_STEMG.html) is retained as a source reference; use the official site if that address is unavailable. These writing practices are not a declaration of STE certification or a complete dictionary audit.

## System-model exchange

Use **OMG Systems Modeling API and Services 1.0** for the API boundary. Keep its UUID identities, Project/Commit model, standard element payloads, endpoint paths, pagination and error responses. Read [API scope and mapping](../en/sysml_api.md) before changes. The five One-Piece trace relations are represented by named standard Dependencies. They do not assert native SysML satisfaction, verification or physical compliance.

Versioned One-Piece JSON remains the single source of truth for requirements, KDPs, detailed parameters and evidence. An API response or report is a projection of those records. Never add a second authoritative copy in a tool-specific guide or an agent prompt.
