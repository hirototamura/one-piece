# Current engineering strategy

This file records concrete strategy and specifications. Keep long-term philosophy and vision in [CORE.md](CORE.md). Changes to CORE.md require prior, explicit human approval for the specific edit.

## Standards and shared methods

Read the shared [engineering standards](../engineering/standards.md), [NASA SE](../engineering/nasa_se.md) and [SpaceX-style SE](../engineering/spacex_se.md) guides for all agents and humans. **ISO/IEC/IEEE 29148:2018 is the first source for requirements standards.** Apply **ASD-STE100 Simplified Technical English where applicable** to English requirements and technical documents. NASA and SpaceX-style methods supplement that standard. Preserve historical records; propose wording changes as new drafts.

## Mandatory platform capabilities

The platform shall support automated verification against versioned requirements. The platform shall support Git-like change history and model diffs. Connect the two: identify affected tests from a configuration change, execute or re-evaluate them, and record evidence against exact requirement and configuration revisions. Keep missing, failed and outdated evidence visible.

See the [restored competitor study](competitor_tradeoff.md) and [design and proposed acceptance criteria](verification_and_diff.md). Historical adoption decisions do not apply. The current store-integrity checks and limited design comparison do not complete these platform capabilities.

## Supporting specifications

- [System model](system_model.md): versioned records, trace relations and evidence scope.
- [SysML API](sysml_api.md): supported standard services and exchange mapping.
- [Verification and diff](verification_and_diff.md): current scope and proposed acceptance criteria.
- [Competitor research](competitor_tradeoff.md): observations without historical adoption decisions.

Add concrete strategy, specification decisions and current implementation priorities here. Link supporting technical detail from this file. Keep canonical engineering requirements and evidence in versioned JSON. Do not move current implementation scope or milestones into CORE.md.

[Japanese strategy](../ja/strategy.md).
