# Competitor research and current design needs

This document restores observations from the [historical study at commit 6576c356](https://github.com/hirototamura/one-piece/blob/6576c356b14c7d287b7ec72a7381d3c7b30b49cd/docs/ja/competitor_tradeoff.md). **Its adoption, deferral and rejection decisions do not apply to the current design.** Its authority assumptions do not change the shared [engineering policy](../engineering/standards.md).

The source cites a market-research PDF covering eight companies on 2026-07-12. That PDF was not checked in this PR. The following observations are historical. They are not a verified list of current product capabilities or performance. Flow and SysGit sources relevant to the user's two mandatory capabilities were checked on 2026-10-11.

## Historical observations

- **Synera:** CAx/PLM connections, analysis and optimization workflows, and supervisor/specialist agents. The reported “76+” connections are a historical count.
- **Dyad:** intent-driven physical models and repeated simulation with physical consistency.
- **Antaris:** Design Studio, digital twins, Flight OS and virtual mission checks before manufacture.
- **SysGit:** machine-readable system models in Git, SSOT, branches, PRs, CI and SysML v2.
- **Flow:** a digital thread that connects requirements to design parameters and threshold checks.
- **Dassault:** Cameo/3DEXPERIENCE, requirement-to-structure extraction and language assistance.
- **Siemens:** NX/Simcenter/Teamcenter and automation from natural language to geometry and CAE.
- **CoLab:** drawing/CAD review, AutoReview and a knowledge graph.

These observations do not select a vendor or architecture. Evaluate scope, execution interfaces, version control, evidence reproducibility and migration with concrete examples.

## Official sources checked for this update

Flow describes linked requirements, systems and tests in its [requirements product page](https://www.flowengineering.com/product/requirements-management). Its [integration page](https://www.flowengineering.com/integrations) describes spreadsheet-value checks, Onshape-derived verification and Python analysis links. Some connectors, including Matlab and SimScale, are marked “Coming Soon”. This study did not run the product or verify its performance.

SysGit describes `.sysml` files stored in Git, branching and merging, and textual and graphical model diffs in its [official IDE article](https://resources.sysgit.io/sysgit-saturday-1-a-purpose-built-collaborative-sysml-v2-ide/). This is the vendor's description. No migration or performance comparison was run.

## Mandatory product intent

The user requires two capabilities: **automated verification against requirements**, and **Git-like change and diff management**. Link these capabilities: a change identifies affected tests, execution produces evidence, and each result refers to exact requirement and configuration revisions. A previous pass shall not transfer to a changed configuration without an applicability check.

One-Piece owns records and evidence. Engineering Agents executes bounded tests. ISO/IEC/IEEE 29148:2018 remains the first requirements reference. Preserve the SysML API boundary. See [design and acceptance criteria](verification_and_diff.md) and the [Japanese study](../ja/competitor_tradeoff.md).
