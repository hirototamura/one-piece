# Project plan — one-piece

Living document. **Revise after** each milestone or major scope decision.

## Vision

Deliver a SaaS that lets **teams of any size**—from individuals and startups through large programs—run disciplined systems engineering for hardware: structured requirements, traceable design, credible verification, and compliance views that stay as approachable as a spreadsheet where that helps.

## Principles

1. **Traceability first** — if it isn’t linked, it didn’t happen.  
2. **Human authority for judgment** — agents accelerate drafting and consistency; experts own baselines.  
3. **Scale-appropriate experience** — the same core graph serves solo builders and enterprise programs; **touchpoints differ by team size** (self-serve and low ceremony vs. governance, audit, supplier packages). **Initial wedge: small teams**—prove depth there before expanding enterprise surface area.  
4. **Normalized data, simple exports** — matrices and supplier packages are projections.  
5. **Interconnected design** — first-class cross-subsystem checks, not an afterthought.  
6. **Tools over bureaucracy** — prefer shared visibility, traceability, and evidence in the product over heavyweight implicit process.  
7. **Iteration with evidence** — allow rapid learn–adjust cycles at derived levels while **customer/mission intent** stays explicit and verified; tighten formality as baselines mature.

## External influences

Industry narratives on **fast hardware iteration with serious V&V** help shape our principles—for example the 2012 SpaceX slide deck *System Engineering: A Traditional Discipline in a Non-traditional Organization* (themes: integration risk is partly experiential; **test what you fly**; **user-level requirements** verified while **lower tiers trade** with test feedback; **development vs qualification vs acceptance** test roles; **tools not rules**). We **do not** copy a specific org structure; we encode patterns that any customer can adopt.

## Phases (suggested)

| Phase | Outcome | Notes |
|-------|---------|--------|
| **P0 — Domain kernel** | Richer `packages/domain` model: requirement levels, artifact stubs, trace relations | Aligns with `docs/INFORMATION_ARCHITECTURE.md` |
| **P1 — Vertical slice API** | CRUD + trace queries for one program; compliance matrix endpoint or export | Pick one persistence store; keep migrations explicit |
| **P2 — Web UI** | Requirements tree, trace explorer, matrix view, review queue | Human-gate UX for baselines |
| **P3 — Agent hooks** | Server-side or worker flows that draft deltas from natural language, always diff-reviewed | Tie to `AGENT.md` handoff contract |
| **P4 — Collaboration** | Organizations, roles, audit log, baseline snapshots | Small teams first; then mid/large programs and formal governance |

Phases are **sequential in dependency** but can overlap in staffing (e.g. UI mockups during P1).

## Near-term backlog (starter)

- [ ] Extend domain model: requirement level, lifecycle, AIV artifact attachment to system level  
- [ ] Define verification activity types (analysis / test / inspection) + report references; optional **test purpose** (development / qualification / acceptance) for lifecycle ramp  
- [ ] Sketch compliance matrix query (rows/columns/status) against normalized traces  
- [ ] Add persistence PoC (SQLite or Postgres) behind a thin repository layer  
- [ ] Document human review states (draft → under_review → baseline) in UI/API terms  

## Risks

| Risk | Mitigation |
|------|------------|
| Model too rigid for diverse industries | Start with configurable **kinds** and optional attributes; avoid hard-coded physics |
| Agents over-claim verification | Separate “draft” vs “baselined” evidence; human sign-off on pass/waive |
| Matrix UX too simple for power users | Offer filters, saved views, CSV/Excel export |

## Success metrics (early)

- Time from blank project to **traceable system + subsystem requirement set** (self-serve)  
- % requirements with **at least one** planned verification path before baseline  
- Human **time to review** a design package (should drop with consistency pre-checks)  

---

*Last updated: 2026-05-10 — principles extended (SpaceX 2012 deck–informed themes).*
