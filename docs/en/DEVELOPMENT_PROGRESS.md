# Development progress log

Append **newest entries at the top**. Keep each entry to a few sentences; link commits or PRs when available.

## 2026-07-17 (spacex-se subagent)

- Added project subagent `.cursor/agents/spacex-se.md` that executes SpaceX-style SE practice from the 2012 SpaceX SE deck (*System Engineering: A Traditional Discipline in a Non-traditional Organization*) plus Hardware DevOps / modular chief-engineer operating patterns.
- Encodes stable top-level intent vs traded KDPs, Plan–Design–Build–Test spirals, Test Like You Fly, development/qualification/acceptance/HITL hierarchy, tools-not-rules integration, and mapping to `docs/*/CORE.md` artifact types.

## 2026-07-11 (documentation-only repository)

- Removed all implementation artifacts: `apps/`, `packages/`, root `package.json`, `package-lock.json`, `pyproject.toml`, and `tsconfig.base.json`.
- Repository scope is now `docs/en/CORE.md`, `docs/ja/CORE.md`, and this log, plus `LICENSE`.
- Updated `CORE.md` and `.gitignore` to drop references to removed code paths.

## 2026-07-11 (remove web app)

- Removed `apps/web` (Vite + React PoC) and the `apps/` workspace from the monorepo.
- Updated root `package.json` and `package-lock.json`.

## 2026-07-11 (docs consolidation)

- Removed `PROJECT_PLAN.md` and `INFORMATION_ARCHITECTURE.md` from `docs/ja/` and `docs/en/`. Living docs are now README indexes plus `development_progress.md`; philosophy and IA content live in `ja/CORE.md` / `en/CORE.md`.
- Updated README and `CORE.md` links across the repository.

## 2026-06-16 (documentation i18n layout)

- Split living docs into `docs/ja/` and `docs/en/`. Moved root `README.md` and `AGENTS.md` under `ja/` and `en/`; root files are now language indexes.

## 2026-06-07 (terminology: requirements)

- Unified Japanese docs on 「要求」 (requirements) to match hardware SE convention; code identifiers such as `Requirement` unchanged.

## 2026-06-07 (README expansion)

- Rewrote `ja/README.md`: Web UI tour, SSOT/actor glossary, ecosystem placement, install/run commands, repository map.

## 2026-06-07 (Apache-2.0 license)

- Added root `LICENSE` (Apache-2.0); declared `Apache-2.0` in `README.md` and `package.json` (root, `packages/domain`, `apps/web`). Added `license = "Apache-2.0"` to four Python `pyproject.toml` files.

## 2026-05-30 (documentation Japanese translation)

- Translated repository Markdown to Japanese for local teams (`ja/README.md`, `ja/AGENTS.md`, `docs/ja/*`, `.cursor/skills/*`, `packages/design-integration/README.md`). Code identifiers, CLI, and paths kept in original form.

## 2026-05-26 (autonomous co-design MVP scaffold)

- Added autonomous co-design domain support: `CoDesignGoal`, `CoDesignIteration`, `CoDesignRun`, `AgentScopePolicy.autonomousCoDesign`, and helpers for review-queue bypass semantics in bounded AI-100 runs.
- Web: new **Co-Design** view with goal input, iteration timeline, live SSOT graph, provenance tail, and replay of autonomous thermal-loop iterations; actor-policy view now surfaces autonomous mode explicitly.
- Python: new `packages/co-design` orchestrator + SQLite persistence, `packages/connectors` SSOS/ROS2 bootstrap ingest CLI, and thermal rejection stand-in analysis in `packages/design-integration` with direct SSOT parameter sync.

## 2026-05-23 (actor boundaries + Excel/Python integration)

- Branch `feature/actor-boundaries-design-integration`: SSOT mutations attributed to **human engineer**, **logic automation**, or **AI agent**; `AgentScopePolicy` (~20% AI default), `SsotProvenanceRecord` with `aiTouchInHumanDomain` warnings.
- Extended `packages/domain` (`DesignArtifact`, `CellCodeBinding`, `IntegrationRun`, policy helpers); new `packages/design-integration` Python package (Excel→Python sync + script runner).
- Web: **Actor boundaries**, **Design integration** views; provenance panels on requirements and parameters.

## 2026-05-19 (web — full SSOT UI)

- `apps/web` reflects graph SSOT: **SSOT graph** explorer, **ICD**, **Design** (parameters + constraints), **CAD** (sync status), cross-node **graph links**, matrix includes constraints as V&amp;V subjects, review queue includes constraints.

## 2026-05-19 (SSOT — ICD, constraints, CAD)

- Confirmed graph-DB SSOT direction: **ICD** per subsystem interface, **design parameters**, **design constraints** (`actsAsFunctionalRequirement` for V&V), **CAD models** with live sync into SSOT.
- Extended `packages/domain` (`EngineeringGraph`, `InterfaceControlDocument`, `DesignParameter`, `DesignConstraint`, `CadModel`, expanded `TraceRelation`); demo program seeded with sample ICD/CAD/constraint.

## 2026-05-19 (SSOT architecture)

- Documented SSOT placement in `docs/INFORMATION_ARCHITECTURE.md`: normalized **program graph** as authority; discipline tools and matrix/Excel as projections; pull/push pattern for automated V&V.

## 2026-05-19 (web PoC)

- Added `apps/web` (Vite + React): requirements tree by level, compliance matrix, configuration selector, human review queue with lifecycle actions; demo program seeded in-memory.
- Extended `packages/domain` with `RequirementLevel`, `Program`, `VerificationActivity`, `MatrixCell`.

## 2026-05-19

- `docs/PROJECT_PLAN.md` **Principles** rewritten around five hardware SE tenets: traceability/records, iteration over perfection, smarter requirements, cross-functional design, test early + automate; prior product-delivery items folded into a short delivery subsection.
- Vision reframed: **accelerate hardware engineering** for all team scales (individual → startup → large program).

## 2026-05-10 (SpaceX 2012 SE deck)

- Read industry handbook-style deck; aligned `AGENTS.md` (engineering philosophy, verification notes, workflow), `docs/PROJECT_PLAN.md` (principles 6–7, external influences), `docs/INFORMATION_ARCHITECTURE.md` (stable vs derived trades, verification rigor table), `.cursor/skills/systems-engineering-saas/SKILL.md`.

## 2026-05-10 (later)

- Mission wording: **all team sizes**; **touchpoints differ by scale**; **small teams first** as GTM wedge. Updated `AGENTS.md`, `docs/PROJECT_PLAN.md`, `docs/INFORMATION_ARCHITECTURE.md`.

## 2026-05-10

- Added `AGENTS.md` for multi-agent orchestration (roles, workflows, human gates).  
- Added `docs/PROJECT_PLAN.md`, `docs/INFORMATION_ARCHITECTURE.md`, and this log.  
- Added project skills: `systems-engineering-saas`, `human-design-review`; Cursor rule pointing agents at repo context.  

---

*Template for future entries:*

## YYYY-MM-DD

- …
