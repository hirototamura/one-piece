# one-piece — Hardware systems-engineering SaaS

A proof-of-concept (PoC) SaaS that manages hardware product **requirements, design, interfaces, and verification** in **one traceable graph** from mission through verification. Targets **teams of any size**, with the roadmap prioritizing **small teams first** and spreadsheet-simple compliance views.

Human engineers own **baselines and judgment**; AI agents assist with drafting, cross-checks, and consistency. This repository is **not production SaaS**—it is a **research and development monorepo** combining the domain model, Web UI PoC, Python integration packages, and agent operating rules.

---

## At a glance (Web UI)

The demo UI in `apps/web` (`npm run dev`) walks a sample in-memory program through 10 views that explore the SSOT (Single Source of Truth).

### 1. SSOT graph — authoritative program graph

Explore requirements, ICDs, design parameters, constraints, CAD, verification activities, and trace edges in **one graph**. Matrices and trees are **projections** of this graph; the SSOT is the authority.

### 2. Requirements — hierarchical requirement tree

Display requirements at `mission` → `system` → `operational` → `subsystem` levels; inspect selected node details, lifecycle (`draft` / `under_review` / `baseline`), and upstream traces. **AIV** (Assembly and Integration Verification) plans attach to system requirements.

### 3. Interfaces (ICD) — subsystem interfaces

Manage **Interface Control Documents** per provider/consumer pair with signals, limits, and units. A starting point for cross-cutting consistency checks.

### 4. Design — parameters and design constraints

List `DesignParameter` (value, unit, bounds, discipline tags) and `DesignConstraint`. Constraints with `actsAsFunctionalRequirement` participate in **allocation and V&V** like functional requirements.

### 5. CAD — model revisions and sync status

Track CAD node revisions, checksums, and sync status on the SSOT. Geometry lives in PLM/object storage; **revisions and extracted parameters sync back to the SSOT on every design change**.

### 6. Design integration — Excel ↔ Python

Sync cell values and `SSOT:PARAM:KEY` markers via `DesignArtifact` (Excel workbooks, Python scripts) and `CellCodeBinding`. **Logic automation** (no AI) updates cells → re-runs scripts → records `IntegrationRun`.

### 7. Co-Design — autonomous design iteration

Given a `CoDesignGoal` (natural-language objective + numeric metrics), AI updates derived parameters within allowed scope, runs analysis between iterations, and syncs timeline, SSOT graph, provenance, and iteration replay.

### 8. Actor boundaries — who changed the SSOT

Every change is attributed to **human engineer**, **logic automation**, or **AI agent**. `AgentScopePolicy` (default ~20% AI) and `SsotProvenanceRecord` provide an audit trail including `aiTouchInHumanDomain` warnings.

### 9. Compliance matrix — requirements ↔ evidence

Rows = requirements (or verification subjects); columns = evidence (test cases, analysis IDs, inspection records); cells = status (planned / passed / failed / waived). UX goal: spreadsheet-simple readability; underlying data comes from normalized traces.

### 10. Review queue — human gate

Review queue to advance drafts or AI proposals to **baseline**. Human sign-off is required before design baselines, waivers, or “verified” claims.

---

## Why one-piece

Hardware programs hide ambiguous requirements, subsystem interface mismatches, and scattered verification evidence until late integration. Real teams run this loop:

1. **Hierarchize intent** (mission → system → operational → subsystem)
2. **Link design and verification plans** with traces
3. **Update derived specs** from build, test, and analysis with rationale
4. **Find gaps** in the compliance matrix; humans baseline

one-piece makes this loop reproducible in **SaaS data model and UI**, with agents drafting and cross-checking by design in code and docs.

**Design principles (excerpt)**


| Principle | Meaning |
| --------- | ------- |
| Traceability and records first | Without links and records, it did not happen |
| Iteration over perfection | Mission intent stays fixed; derived specs update with evidence |
| Smarter requirements | Reduce ambiguity; write verifiable statements |
| Cross-disciplinary design | Mechanical, electrical, thermal, software, ops, test in one graph |
| Test early; automate | Run development tests early; humans focus on baselines and anomalies |


See [docs/en/PROJECT_PLAN.md](../docs/en/PROJECT_PLAN.md) and [en/AGENT.md](./AGENT.md) for details.

---

## Core concepts (glossary)


| Term | Description |
| ---- | ----------- |
| **SSOT** | Per-program normalized graph (DB is authority); matrices and trees are projections |
| **Program** | Engineering context for one product/program (configurations V1/V2, etc.) |
| **Requirement level** | `mission` / `system` / `operational` / `subsystem` |
| **AIV** | Assembly and Integration Verification — system-level integration verification plan |
| **ICD** | Interface Control Document — agreed subsystem interface |
| **Design package** | Subsystem design description + supporting analysis |
| **Verification activity** | Analysis, test, or inspection (linked to reports and evidence) |
| **Compliance matrix** | Requirements ↔ evidence grid (simple status + artifact refs) |
| **AgentScopePolicy** | Caps on node kinds and criticality AI may change (`autonomousCoDesign` allows 100% in PoC) |
| **CoDesignRun** | Goal-driven autonomous design loop (iterations, metrics, convergence) |
| **Logic automation** | Deterministic sync without LLM (Excel sync, CI tests, connector webhooks) |


**Stable intent vs derived trades**

- **Mission / customer / user intent** — tracked and verified
- **Derived specs and lower requirements** — tradable during design, but **must link** to rationale, decisions, and waivers

### Requirement graph (default flow)

```text
[Mission requirements]
        |
        v
[System requirements] -----> [AIV plan]
        |
   +----+----+
   v         v
[Operational]  [Subsystem requirements]
                      |
                      +--> [Design package + analysis]
                      +--> [Verification plan + platform needs]
```

### Three SSOT mutation actors


| Actor | Role | Examples |
| ----- | ---- | -------- |
| **Human engineer** | Baselines, major judgment, real-world interface | Requirement edits, waiver approval |
| **Logic automation** | Reproducible, deterministic | `one-piece-sync`, test runners, SSOS ingestion |
| **AI agent** | Drafts within policy (default ~20%) | Requirement text, parameter proposals, co-design iterations |


---

## Position in the repo vs engineering_agents / SSOS

```text
[ one-piece (this repository) ]
  packages/domain     … TypeScript domain model (SSOT types)
  apps/web            … SSOT explorer, matrix, review UI PoC
  packages/co-design  … autonomous design loop orchestrator
  packages/design-integration … Excel ↔ Python sync
  packages/connectors … reverse ingestion from external sources (SSOS, etc.)

[ Integrations (research / in progress) ]
  engineering_agents  … ECLSS anomaly simulation + design proposal JSONL
  Space Station OS      … orbital ops software mock / future adapter
```


| Area | Status | Reference |
| ---- | ------ | --------- |
| Domain kernel (`packages/domain`) | **Available** | [docs/en/INFORMATION_ARCHITECTURE.md](../docs/en/INFORMATION_ARCHITECTURE.md) |
| Web UI PoC (`apps/web`) | **Available** (in-memory demo) | This README [Web UI](#at-a-glance-web-ui) |
| Excel/Python integration | **Available** (PoC) | [packages/design-integration/README.md](../packages/design-integration/README.md) |
| Autonomous co-design loop | **Available** (PoC) | [packages/co-design/README.md](../packages/co-design/README.md) |
| SSOS reverse ingestion | **Stub / CLI** | [packages/connectors/README.md](../packages/connectors/README.md) |
| Production API, persistent DB, multi-tenant | **Not implemented** | [docs/en/PROJECT_PLAN.md](../docs/en/PROJECT_PLAN.md) |


[engineering_agents](https://github.com/hirototamura/engineering_agents) simulates operational anomalies → team decisions → permanent design proposals and is intended to export **design proposal provenance** in one-piece format (see `docs/one-piece-integration.md` in that repo).

---

## Documentation


| Document | Audience | Contents |
| -------- | -------- | -------- |
| [en/AGENT.md](./AGENT.md) | Agents, contributors | Roles, workflows, human gates, documentation duty |
| [docs/en/PROJECT_PLAN.md](../docs/en/PROJECT_PLAN.md) | Product, engineering | Phases, backlog, risks, success metrics |
| [docs/en/INFORMATION_ARCHITECTURE.md](../docs/en/INFORMATION_ARCHITECTURE.md) | Modelers, architects | SSOT, artifacts, trace, matrix, co-design |
| [docs/en/DEVELOPMENT_PROGRESS.md](../docs/en/DEVELOPMENT_PROGRESS.md) | Everyone | Chronological change log |
| [docs/en/README.md](../docs/en/README.md) | Everyone | Index of the above |
| [ja/README.md](../ja/README.md) | 日本語読者 | 日本語ドキュメント索引 |


**Cursor project skills**


| Skill | Use |
| ----- | --- |
| `.cursor/skills/systems-engineering-saas/` | Requirement hierarchy, V&V, matrix, domain type extension |
| `.cursor/skills/human-design-review/` | Design baseline, human judgment on analysis trust |


---

## Prerequisites

- **Node.js 20+** (Web UI, `packages/domain`)
- **npm** (workspace monorepo)
- **Python 3.11+** (`packages/co-design` / `design-integration` / `connectors`)
- **uv** or **pip** (local Python package install)

---

## Installation (from scratch)

### 1. Clone the repository

```bash
git clone https://github.com/hirototamura/one-piece.git
cd one-piece
```

### 2. Node dependencies and domain build

```bash
npm install
npm run build -w @one-piece/domain
```

### 3. Start the Web UI

```bash
npm run dev
```

Open `http://localhost:5173` in a browser. Switch among the 10 sidebar views.

### 4. Python packages (optional)

Each package is independent. Example: design integration PoC

```bash
cd packages/design-integration
uv sync          # or: pip install -e .
uv run pytest
```

Similarly for `packages/co-design` and `packages/connectors` with `uv sync` / `pip install -e .`.

---

## How to run

### Web UI (demo program)

```bash
npm run dev
# → http://localhost:5173
```

- Switch V1/V2 via the configuration selector
- **Co-Design** view: start/stop autonomous loop, replay iterations
- **Review queue**: lifecycle transitions (human-gate UX)

### Domain types — build and typecheck

```bash
npm run build -w @one-piece/domain
npm run typecheck -w @one-piece/domain   # if script exists in package.json
```

### Excel ↔ Python sync (`one-piece-sync`)

```bash
cd packages/design-integration
uv run python examples/create_workbook.py
uv run one-piece-sync \
  --workbook examples/propulsion_budget.xlsx \
  --script examples/thrust_margin.py \
  --bind "Inputs!B2:P-VBUS:P-VBUS:VBUS" \
  --bind "Inputs!B3:P-M-MOTOR:P-M-MOTOR:MOTOR_MASS_KG"
```

Thermal rejection stand-in analysis: `examples/thermal_rejection.py` (callable from co-design loop).

### Autonomous co-design CLI

```bash
cd packages/co-design
python -m one_piece_codesign.cli \
  --program ../../tmp/program.json \
  --output ../../tmp/program-out.json \
  --db ../../tmp/codesign.db
```

### External source ingestion (SSOS stub)

```bash
cd packages/connectors
python -m one_piece_connectors.cli \
  --source ssos \
  --path /path/to/space_station_os \
  --output /tmp/ssos-graph.json
```

---

## Repository layout


| Path | Purpose |
| ---- | ------- |
| `packages/domain/` | Shared domain model (requirements, graph, trace, co-design, policy) |
| `apps/web/` | Vite + React Web UI PoC |
| `packages/design-integration/` | Excel ↔ Python bindings, logic-automation runner |
| `packages/co-design/` | Autonomous design loop orchestrator + SQLite persistence |
| `packages/connectors/` | Reverse-ingestion CLI for SSOS, etc. |
| `docs/ja/`, `docs/en/` | Living design docs (plan, IA, progress) per language |
| `.cursor/skills/` | Domain + human-review agent skills |
| `.cursor/rules/` | Short pointers for agents |


**Dependency sketch:** `apps/web` → `packages/domain`; Python packages exchange domain JSON via files at PoC stage.

**Roadmap (summary)**


| Phase | Outcome |
| ----- | ------- |
| P0 Domain kernel | Rich `packages/domain` (in progress) |
| P1 Vertical-slice API | CRUD + trace queries + matrix API |
| P2 Web UI | Requirement tree, matrix, review (PoC done; persistence next) |
| P3 Agent hooks | Server-side draft → diff review |
| P4 Collaboration | Orgs, roles, audit log, baseline snapshots |


---

## License

[Apache License 2.0](../LICENSE)
