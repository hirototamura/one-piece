---
name: systems-engineering-saas
description: >-
  Models requirements hierarchies, AIV plans, subsystem design packages, verification
  (analysis/test/inspection), verification platform needs, and compliance matrices for
  the one-piece hardware systems-engineering SaaS. Use when elaborating requirements,
  traceability, V&V plans, platform specifications, or extending packages/domain types.
---

# Systems engineering SaaS (one-piece)

## Scope

Apply when working on domain types, APIs, UX, or agent prompts that touch **requirements → design → verification → evidence**.

## Requirement levels (top to bottom)

1. **Mission requirements** — program intent  
2. **System requirements** — whole-system behavior and constraints; include **AIV (Assembly and Integration Verification)** plan  
3. **Operational requirements** — use, deployment, logistics, maintenance  
4. **Subsystem requirements** — allocations and constraints per subsystem  

**System requirements** drive **both** operational and subsystem requirements. Represent branching with explicit trace links, not implicit ordering alone.

## Stable intent vs derived trades

Keep **user / mission / customer-facing** intent verified end-to-end. **Derived** lower-level reqs and specs may change when test or analysis informs better trades—always attach **traceable rationale** (decision, analysis ID, test ID, or waiver). See [AGENT.md](../../AGENT.md) engineering philosophy.

## Test rigor and integration

- Prefer **testable** designs; integrated runs (e.g. HITL-style) map to verification activities + **verification platform** artifacts.  
- Where useful, tag tests with **purpose**: development (learn margins) → qualification (bounded worst-case) → acceptance (workmanship)—formality ramps with lifecycle.

## Subsystem requirements outputs

Subsystem requirements must connect to:

- **Subsystem design** (design packages + **analysis results**)  
- **Subsystem verification activity plan** (analysis, test, inspection—each with **reports**)  
- **Verification platform requirements** and **specifications**

## Consistency

Subsystem designs are interconnected. After substantive edits:

- Check **lateral** consistency (interfaces, environments, shared assumptions)  
- Check **upward** alignment to system and mission requirements  

## Compliance matrix

Target UX: **Excel-simple**. Rows = requirements (or verification objectives); columns = evidence; cells = status + link to artifact revision. Prefer normalized storage with matrix as a **view/export**.

## Source of truth

- Orchestration: [AGENT.md](../../AGENT.md)  
- Living architecture: [docs/INFORMATION_ARCHITECTURE.md](../../docs/INFORMATION_ARCHITECTURE.md)  

After meaningful changes, append [docs/DEVELOPMENT_PROGRESS.md](../../docs/DEVELOPMENT_PROGRESS.md).
