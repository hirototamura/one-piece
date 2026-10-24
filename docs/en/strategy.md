# Current engineering strategy

This file records concrete strategy and specifications. Keep long-term philosophy and vision in [CORE.md](CORE.md). Changes to CORE.md require prior, explicit human approval for the specific edit.

## Standards and shared methods

Read the shared [engineering standards](../engineering/standards.md), [NASA SE](../engineering/nasa_se.md) and [SpaceX-style SE](../engineering/spacex_se.md) guides for all agents and humans. Apply this order: **ISO/IEC/IEEE 29148:2018 first; applicable NASA standards and requirements guidance second; ASD-STE100 Simplified Technical English third where compatible.** Use `shall` for English requirement statements. SpaceX-style methods supplement this order. Preserve historical records; propose wording changes as new drafts.

## Mandatory platform capabilities

The platform shall support automated verification against versioned requirements. The platform shall support Git-like change history and model diffs. For each configuration change, identify affected tests. Run the tests or evaluate the saved data again. Link each result to exact requirement and configuration revisions. Keep missing, failed and outdated evidence visible.

See the [restored competitor study](competitor_tradeoff.md) and [design and proposed acceptance criteria](verification_and_diff.md). Historical adoption decisions do not apply. The current store-integrity checks and limited design comparison do not complete these platform capabilities.

## Requirement language and model revisions

Write English requirements first, then translate them into Japanese. Use the [shared writing profile](../engineering/standards.md) and retain exact source revisions.

The [Cube requirements](balancing_cube_requirements.md) separate test obligations from organizational containers. Human review on 2026-10-19 accepted 22 statements and the allocation split into 8 functions and 10 components. The versioned review decision and hashed baseline record that scope. Old evidence keeps its original revision targets; planned verification cases remain unrun. See [v0.3.0 release notes](reviewed_cube_release.md).

## Supporting specifications

- [Requirements explorer](requirements_explorer.md): canonical revision selection, graph inspection and browser-local review proposals.
- [Dataset storage](dataset_storage.md): Git-tracked retrieval catalogs and immutable Release evidence shared across environments.
- [System model](system_model.md): versioned records, trace relations and evidence scope.
- [Cube configuration catalogue](cube_configuration_catalogue.md): reviewed, executable, historical and BOM-reference roles with exact revisions.
- [SysML API](sysml_api.md): supported standard services and exchange mapping.
- [Verification and diff](verification_and_diff.md): current scope and proposed acceptance criteria.
- [Competitor research](competitor_tradeoff.md): observations without historical adoption decisions.
- [Report collection and campaigns](report_collection.md): derived bilingual views, preview ownership and scoped numerical evidence.
- [Eight-corner mission and first trial](bottom_corner_trial.md): fixed lower-face mounts, controller ancestry and evidence limits.

Add concrete strategy, specification decisions and current implementation priorities here. Link supporting technical detail from this file. Keep canonical engineering requirements and evidence in versioned JSON. Do not move current implementation scope or milestones into CORE.md.

[Japanese strategy](../ja/strategy.md).
