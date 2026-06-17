# Project plan — one-piece

Living document. **Revise after** each milestone or major scope decision.

## Vision

Deliver a product that **accelerates hardware engineering** for **teams of any size**—from individuals and startups through large programs—through disciplined systems engineering: structured requirements, traceable design, credible verification, and compliance views that stay as approachable as a spreadsheet where that helps.

## Principles

Hardware systems engineering principles that one-piece is built to reinforce:

1. **Traceability and records first** — Traceability and a durable record of what mattered (decisions, requirements, evidence, waivers) are the foundation for everything else. If it isn’t linked and recorded, it didn’t happen.

2. **Iteration dwarfs perfection** — Learn fast from build, test, and integration; refine derived design and lower-level requirements with evidence. Mission and customer intent stay explicit; formality ramps as baselines mature.

3. **Make requirements less dumb** — Requirements should be clear, testable, and worth verifying—not placeholders or process theater. The product (and agents) should push clarity, challenge ambiguity, and keep intent tied to real verification.

4. **Cross-functional, multidisciplinary design** — Interfaces, budgets, and integration risks are first-class across mechanical, electrical, thermal, software, operations, and test—not siloed subsystems reconciled at the end.

5. **Test early; automate tests** — Plan verification from the start; run development tests early and often. Prefer repeatable, automated checks where they buy signal; reserve human judgment for baselines, anomalies, and pass/waive.

**How we build the product (delivery):** experts **baseline** what agents draft; the **same core graph** serves solo builders and large programs (**touchpoints differ by team size**—**small teams first** on the roadmap); compliance matrices and supplier packages are **projections** of normalized traces, not a parallel truth; prefer **tools and visible evidence** over heavyweight implicit process.

## External influences

Industry narratives on **fast hardware iteration with serious V&V** help shape our principles—for example the 2012 SpaceX slide deck *System Engineering: A Traditional Discipline in a Non-traditional Organization* (themes: integration risk is partly experiential; **test what you fly**; **user-level requirements** verified while **lower tiers trade** with test feedback; **development vs qualification vs acceptance** test roles; **tools not rules**). We **do not** copy a specific org structure; we encode patterns that any customer can adopt.

## Phases (suggested)

| Phase | Outcome | Notes |
|-------|---------|--------|
| **P0 — Domain kernel** | Richer `packages/domain` model: requirement levels, artifact stubs, trace relations | Aligns with `docs/en/INFORMATION_ARCHITECTURE.md` |
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

*Last updated: 2026-05-19 — hardware SE principles (traceability, iteration, smart requirements, cross-discipline, test early).*
