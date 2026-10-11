# Shared engineering standards

This policy applies to humans and every agent, including Codex, Claude and Cursor. The canonical guides are [NASA SE](nasa_se.md) and [SpaceX-style SE](spacex_se.md). Tool-specific files are entry points, not separate policies.

Follow the [document-governance rules](../../AGENTS.md#protected-philosophy-and-document-names) before edits. CORE.md holds protected long-term philosophy. Current strategy and specification choices belong in [strategy.md](../en/strategy.md) / [日本語](../ja/strategy.md).

## Requirements: source priority

Apply sources in this order: **(1) ISO/IEC/IEEE 29148:2018, Systems and software engineering — Life cycle processes — Requirements engineering**, (2) applicable NASA standards and systems engineering requirements guidance, then (3) ASD-STE100 where it applies to English writing. SpaceX-style methods can supplement this order. Do not replace the requirements standard with a company handbook. Record the standard edition and applicable clause when the licensed text is available. The [ISO catalogue](https://www.iso.org/standard/72089.html) identifies the standard; it does not supply its full normative text. Do not invent clause numbers or claim full compliance from this policy or an automated check.

For each new or revised requirement, record its stable ID, revision, responsible product, source, rationale, approval state, parent trace, conditions, measurable acceptance criteria, units and verification method. State one obligation with a clear subject. Separate requirements from assumptions, design choices and results. Identify missing information as unresolved. Preserve historical source wording and status; propose corrections as new drafts. Humans approve requirements, evaluation contracts and adopted baselines.

## Technical English

Use `shall` for each normative English requirement statement. NASA's [Appendix C](https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/) identifies `shall` as the requirement modal. Apply ASD-STE100 Issue 9 where it does not conflict with the higher-priority sources. Issue 9 lists `shall` as unapproved and gives `must` as its alternative; the project uses `shall` because of the stated source priority and does not claim complete STE compliance. Use short sentences, active voice, consistent defined terms and explicit units. Keep one obligation per sentence. Avoid ambiguous pronouns and unnecessary synonyms. Mark each statement as a requirement in its structured data. Preserve historical wording, standard identifiers, equations, API names and defined technical terms. Do not change a requirement's meaning to simplify its language. Write the English source first, then translate that source into Japanese. Keep the source revision and translation together.

Consult the official [ASD-STE100 site](https://www.asd-ste100.org/) and [FAQ](https://www.asd-ste100.org/STE_faq.html) for the current issue and access to the rules and dictionary. The [Issue 9 rules and dictionary](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf), dated 15 January 2025, were consulted for the Cube revision. Rules 1.5–1.11 allow defined technical names; rule 3.6 covers active voice; rules 4.1 and 6.1 cover short, clear sentences and one subject per sentence; rule 6.3 limits descriptive sentences to 25 words. The requested [STEMG page](https://asd-ste100.org/ASD_STEMG.html) is retained as a source reference; use the official site if that address is unavailable. The modal choice follows the declared priority and is an explicit exception to the Issue 9 dictionary preference. These writing practices are not a declaration of STE certification or a complete dictionary audit.

## System-model exchange

Use **OMG Systems Modeling API and Services 1.0** for the API boundary. Keep its UUID identities, Project/Commit model, standard element payloads, endpoint paths, pagination and error responses. Read [API scope and mapping](../en/sysml_api.md) before changes. The five One-Piece trace relations are represented by named standard Dependencies. They do not assert native SysML satisfaction, verification or physical compliance.

Versioned One-Piece JSON remains the single source of truth for requirements, KDPs, detailed parameters and evidence. An API response or report is a projection of those records. Never add a second authoritative copy in a tool-specific guide or an agent prompt.
