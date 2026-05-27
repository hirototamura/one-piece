# Agent orchestration — one-piece

This file is the **control tower** for AI agents working on one-piece: a systems-engineering SaaS for **teams of any size**—requirements, design, verification, and traceability for hardware. Humans remain the **domain authority**; agents draft, cross-check, and keep artifacts consistent.

## North star

Enable **every scale** of builder—individuals, startups, labs, and large programs—to run **serious systems engineering** (mission through verification) using structured artifacts, traceability, and compliance views that can stay as approachable as an Excel matrix. **How they meet the platform differs by team size** (self-serve vs. governance-heavy programs); the product should grow **touchpoints** for larger orgs without abandoning clarity for small ones.

**Go-to-market:** ship depth with **small teams first**; then harden collaboration, audit, and enterprise workflows as larger customers need them.

## Team scale and touchpoints

| Scale | Typical touchpoints (non-exhaustive) |
|-------|--------------------------------------|
| Small / solo | Fast capture, agent-assisted drafting, minimal ceremony, simple matrix exports |
| Mid-size | Shared baselines, clearer roles, richer review queues |
| Large / regulated | Strong audit trails, formal sign-off, supplier evidence packages, org-wide reporting |

Same underlying artifact model; **different emphasis in UX, permissions, and integrations**—design so those layers can evolve without rewriting the core graph.

## Engineering philosophy (informed practice)

Ideas below are **adapted from common industry practice**, including the widely circulated 2012 SpaceX slide deck *System Engineering: A Traditional Discipline in a Non-traditional Organization* (often labeled a “systems engineering handbook”). one-piece is **vendor-neutral**; we take the patterns that transfer to SaaS, not any single company’s org chart.

1. **Premise** — Systems engineering exists to catch integration issues early, yet new systems always surprise you. The platform should support **learning from integration and test**, not only from upfront decomposition.

2. **Responsibility over checkbox process** — Process cannot replace engineering judgment. Prefer **visible traceability, reviews, and tools** over opaque rule walls.

3. **Stable intent vs derived trades** — Treat **mission / customer / user-level intent** as **tracked and verified**. **Derived** specifications and lower-level requirements may be **traded and optimized during design**; every material trade must leave an **audit trail** (link to rationale, analysis, decision, or waiver)—never silent drift.

4. **Iteration and formality** — Early cycles favor speed and evidence from **build–test** (or analysis) feedback; **documentation and gate weight increase** as artifacts move toward baseline and production-like maturity.

5. **Test what you fly** — Design for **testability**; plan integrated verification (hardware–software, multi-subsystem) and **service-like** conditions where program risk warrants it. Verification platform requirements should reflect **real environments** and integration rigs, not only bench checks.

6. **Test purpose taxonomy** — Where useful, classify test activities (e.g. **development** — explore margins / find weaknesses; **qualification** — demonstrate performance to bounded environments and margins; **acceptance** — workmanship and repeatability). Formality and repeat expectations can rise with maturity. This complements analysis and inspection.

7. **Tools, not bureaucracy** — Discussion, integration status, and evidence should live in **modern collaborative tools** (this product), analogous to “forums that behave more like networks than static control boards”—still under human ownership of baselines.

## Repository map

| Area | Path | Notes |
|------|------|--------|
| Domain types ( evolving ) | `packages/domain/` | Requirements, elements, traces—extend as the information model grows |
| Apps (future) | `apps/` | API, web UI, workers |
| Living product docs | `docs/` | Plan, information architecture, progress log—**update as development advances** |
| Project skills | `.cursor/skills/` | Domain workflows and human-review gates |
| Cursor rules | `.cursor/rules/` | Short pointers so agents load project context |

When touching types or APIs, prefer extending `packages/domain` before inventing parallel shapes in apps.

## Core artifact types (SaaS scope)

The product centers on these **first-class artifacts** (each versioned, reviewable, baselined where appropriate):

1. **Requirements** (hierarchical; see `docs/INFORMATION_ARCHITECTURE.md`)
2. **Specifications** (normative detail derived from / supporting requirements)
3. **Verification plan** (what will be verified, at which level, and how success is judged)
4. **Verification test cases** (executable / observable instances of verification)
5. **Verification platform requirements** (facilities, equipment, software, sensors needed to run V&V)
6. **Design documents** (subsystem design packages, interfaces, budgets)
7. **Analysis results** (reports backing design and verification-by-analysis)

Agents **draft** these; humans **baseline** them after review.

## Requirements hierarchy and trace rules

**Order from top to bottom** (parent drives children):

1. **Mission requirements** — why the system exists; success at the enterprise / program level  
2. **System requirements** — what the system must do / endure as a whole  
3. **Operational requirements** — how the system is used, deployed, maintained, and operated  
4. **Subsystem requirements** — bounded allocations and constraints per subsystem  

**Branching (explicit):**

- **System requirements** carry an **Assembly and Integration Verification (AIV)** plan (how the integrated system is shown to meet system intent).  
- **System requirements** drive **both** **operational requirements** and **subsystem requirements** (not only a single “next row” in a table—use trace links to make the graph explicit).

**Subsystem requirements** drive:

- Subsystem **design** (design packages + analysis)  
- Subsystem **verification activity plan** (analysis, test, inspection)  
- **Verification platform requirements** and **specifications** (what must exist to execute that plan)

Every parent→child relationship should be **traceable** (`derives_from` / `satisfies` as appropriate in `packages/domain`).

## Design consistency and human judgment

Subsystem designs are **tightly coupled**. Agents must:

- Run **cross-subsystem consistency checks** (interfaces, budgets, shared environments, timing, safety, EMC assumptions, etc.)  
- Check **upward alignment** to system and mission requirements  

**Critical:** Agents do **not** replace domain experts. For design decisions and analysis credibility, route through **Human engineering judgment** (see skill `human-design-review`). The product should surface **review tasks**, **assumptions**, and **residual risks** for humans to accept or reject.

## Verification and compliance

Subsystem verification activities include **analysis**, **test**, and **inspection**. Each activity produces a **report** artifact. Tests may optionally carry a **purpose** (development / qualification / acceptance) to match how rigor ramps with lifecycle; integrated **HITL**-style runs are modeled via verification activities plus **verification platform** specs.

**Compliance checks** are modeled as a **matrix**: rows = requirements (or verification objectives), columns = evidence (test case, analysis ID, inspection record), cells = status (e.g. planned / passed / failed / waived) + link to artifact. The UX target: **Excel-simple**; the data model can be normalized underneath.

## Agent roles (subagent / responsibility split)

Use these roles when spawning subagents or parallel tasks. One “orchestrator” conversation should assign work in **thin vertical slices** (e.g. “extend domain types for verification platform” + “update docs”) rather than monolithic dumps.

| Role | Responsibility |
|------|----------------|
| **Orchestrator** | Breaks work into slices, enforces traceability rules, updates `docs/DEVELOPMENT_PROGRESS.md`, resolves conflicts between agents, and may run bounded `CoDesignRun` loops in AI-100 mode for derived/standard-tier exploration |
| **Requirements agent** | Mission→system→operational→subsystem flow; AIV plan content at system level; trace graph health |
| **Architecture / ICD agent** | System elements, interfaces, design packages; consistency checks across subsystems |
| **Verification agent** | Plans, test cases, platform needs, evidence matrix, report templates; in co-design loops, reads analysis results and updates closure status without claiming human certification |
| **Domain model agent** | TypeScript domain types, invariants, migration notes in domain package |
| **Human gatekeeper** | Not an LLM—checklist for when to stop and require human sign-off (design baselines, waiver authority) |

**Handoff contract** (every slice should end with):

- What changed (files + intent)  
- Trace impact (new or updated links)  
- Open risks / assumptions for human review  
- Suggested next slice  

## Workflows (happy path)

1. **Elaborate requirements top-down** with explicit parent/child traces.  
2. Attach **AIV** at system level; ensure operational and subsystem sets both trace to system.  
3. For each subsystem: design package + verification activity plan + platform needs.  
4. Run **consistency pass** across subsystems and upward to system/mission.  
5. **Short-loop feedback** — where iteration is cheap, use development tests and analysis to update derived specs and trades; record trace deltas.  
6. For cheap, bounded design trades, the orchestrator may enter **autonomous co-design** mode: AI mutates allowed derived/standard nodes, `logic_automation` executes analysis, and each iteration records provenance plus evidence links.  
7. Generate / update **compliance matrix** from traces + verification state.  
8. **Human review** at design baselines and before “verified” claims.

**Autonomous co-design caveat:** a fast loop can bypass the review queue for active exploratory iterations, but it does **not** replace the human gatekeeper for released baselines, waived checks, or external “verified” statements.

## Documentation duty

Any agent completing meaningful work must:

- Append a short entry to `docs/DEVELOPMENT_PROGRESS.md` (date, summary, links to PRs/commits if applicable)  
- If the information model or workflows shift, update `docs/INFORMATION_ARCHITECTURE.md` or `docs/PROJECT_PLAN.md` in the same change set when practical  

## Skills to load

| Situation | Skill |
|-----------|--------|
| Modeling requirements, V&V, platform needs, matrices | `.cursor/skills/systems-engineering-saas/SKILL.md` |
| Design baseline, expert judgment, credibility of analysis | `.cursor/skills/human-design-review/SKILL.md` |

## Glossary (quick)

- **AIV** — Assembly and Integration Verification (system-level integrated proof)  
- **Design package** — Subsystem design description + supporting analysis results  
- **Compliance matrix** — Requirement ↔ evidence grid with simple statuses  

---

*Version: 0.2 — see `docs/PROJECT_PLAN.md` (external influences) and `docs/INFORMATION_ARCHITECTURE.md`.*
