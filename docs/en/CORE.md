# Central philosophy of One Piece Engineering

This file records the central philosophy of One Piece Engineering.

## Project mission

Engineer systems that can reach space and evolve on their own.

To that end, we first build a process for developing systems autonomously.

## North star

- **AI Systems Engineering as a Service (SEaaS)** for hardware—covering **engineering** requirements, design, verification, and traceability.

- A tool used by builders at **every scale** developing **innovative hardware**—individuals, startups, labs, and large programs.

- **Touchpoints with the platform differ by team size** (self-serve vs. governance-heavy programs). Grow **touchpoints** for larger organizations without abandoning clarity for small teams.

- Primary work objects: requirements management, system-model construction, automated verification and updates, and structured artifacts linked to the system model.

- Agent-generated outputs must be explainable through the system model and documentation.

- **Domain authority** between humans and agents is adjustable. When humans hold 100% authority, agents draft, cross-check, and maintain artifact consistency.

- Agents **transfer human expertise** by progressively learning the specialized knowledge humans hold.

- When agents hold 100% authority, they run the full workflow without human intervention to iterate hypotheses at high speed.

## Engineering philosophy

The following is **adapted from common industry practice** (including the widely circulated 2012 SpaceX slide deck *System Engineering: A Traditional Discipline in a Non-traditional Organization*, often labeled a “systems engineering handbook”). one-piece is **vendor-neutral**—we adopt patterns that transfer to SaaS, not any single company’s org chart.

1. **Premise** — Systems engineering exists to catch integration issues early, yet taking on new systems always brings surprises. The platform should support **learning from integration and test**, not only from upfront decomposition.
2. **Traceability and record first** — Traceability and a durable record of what mattered (decisions, requirements, evidence, waivers) underpin everything else. Without links and records, it might as well not have happened.
3. **Iteration over perfection** — Learn fast from build, test, and integration; refine derived design and lower-level requirements with evidence. Keep mission and customer intent explicit; formality rises as baselines mature.
4. **Smarter requirements** — Requirements should be clear, verifiable, and worth verifying—not placeholders or theater. The product (and agents) should drive clarification, challenge ambiguity, and tie intent to real verification.
5. **Stable intent vs derived trades** — Treat **mission / customer / user-level intent** as **tracked and verified**. **Derived** specifications and lower-level requirements may be **traded and optimized during design**; every material trade must leave an **audit trail** (link to rationale, analysis, decision, or waiver)—never silent drift.
6. **Test what you fly** — Design for **testability**; plan integrated verification (hardware–software, multi-subsystem) and **service-like** conditions where program risk warrants it. Verification platform requirements should reflect **real environments** and integration rigs, not only bench checks.
7. **Cross-disciplinary design** — Interfaces, budgets, and integration risk are first-class across mechanical, electrical, thermal, software, operations, and test—do not reconcile in silos at the end.
8. **Test purpose taxonomy** — Where useful, classify test activities (e.g. **development** — explore margins / find weaknesses; **qualification** — demonstrate performance to bounded environments and margins; **acceptance** — workmanship and repeatability). Formality and repeat expectations can rise with maturity. This complements analysis and inspection.
9. **Test early; automate tests** — Plan verification from the start; run development tests early and often. Prefer repeatable automated checks where signal is available; leave baselines, anomalies, and pass/waive to human judgment.
10. **Tools, not bureaucracy** — Discussion, integration status, and evidence should live in **modern collaborative tools**. Analogous to “forums that behave more like networks than static control boards”—still under human ownership of baselines.



## Core artifact types

**First-class artifacts** at the center of the product (each versioned, reviewable, and baselined when needed):

1. **Requirements** (hierarchical; see [Requirement hierarchy and trace rules](#requirement-hierarchy-and-trace-rules) below)
2. **Specifications** (normative detail derived from or supporting requirements)
3. **Verification plan** (what to verify at which level, and how success is judged)
4. **Verification test cases** (executable / observable instances of verification)
5. **Verification platform requirements** (facilities, equipment, software, and sensors needed to execute V&V)
6. **Design documents** (subsystem design packages, interfaces, budgets)
7. **Analysis results** (reports backing design and analysis-based verification)

Agents **draft**; humans **baseline** after review.

## Requirement hierarchy and trace rules

**Top to bottom** (parent drives child):

1. **Mission requirements** — why the system exists; enterprise / program-level success
2. **System requirements** — what the whole system must meet / withstand
3. **Operational requirements** — how the system is used, deployed, maintained, and operated
4. **Subsystem requirements** — allocation and constraints per subsystem

**Branching:**

- **System requirements** carry an **Assembly and Integration Verification (AIV)** plan (how integrated system proof satisfies system intent).
- **System requirements** drive **both** **operational requirements** and **subsystem requirements** (not only the “next row” in a table—make the graph explicit with trace links).

**Subsystem requirements** drive:

- Subsystem **design** (design package + analysis)
- Subsystem **verification activity plans** (analysis, test, inspection)
- **Verification platform requirements** and **specifications** (what must exist to execute those plans)

Every parent→child relationship is **traceable** (appropriate `derives_from` / `satisfies` links in the system model).

## Design consistency and human judgment

Subsystem design is **tightly coupled**. Agents should:

- Run **cross-subsystem consistency checks** (interfaces, budgets, shared environments, timing, safety, EMC assumptions, etc.)
- Check **upward alignment** to system and mission requirements

**Critical:** Domain experts **always take precedence** over agents. Route design decisions and analysis credibility through **Human engineering judgment**. The product should surface **review tasks**, **assumptions**, and **residual risks** for humans to accept or reject. In agent-100% mode, prepare domain agents to virtually fill gaps left by domain experts.

## Verification and compliance

Subsystem verification activities include **analysis**, **test**, and **inspection**. Each activity produces a **report** artifact. Tests may optionally carry a **purpose** (development / qualification / acceptance) to ramp rigor with lifecycle. Integrated execution is modeled via verification activities plus **verification platform** specifications.
