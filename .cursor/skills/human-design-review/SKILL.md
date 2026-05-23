---
name: human-design-review
description: >-
  Routes subsystem design and analysis credibility to human engineering judgment for
  the one-piece SaaS. Use when baselining design packages, accepting analysis results,
  waiving verification, or when agents lack domain-specific safety or performance context.
---

# Human design review (one-piece)

## When humans must be in the loop

Agents draft; **humans baseline**. Require explicit human review before:

- **Baselining** a subsystem design package or ICD-affecting change  
- Marking **analysis results** as authoritative for load, safety, EMC, thermal, or mission-critical margins  
- **Waiving** or **deferring** verification  
- Overriding a **failed** compliance matrix cell  
- Shipping claims like “verified” or “requirements met” externally  

## What to surface for reviewers

Provide a tight packet:

1. **Delta summary** — what changed vs last baseline  
2. **Trace impact** — which requirements / interfaces are touched  
3. **Assumptions & sensitivities** — numbers, models, environmental bounds  
4. **Open consistency findings** — cross-subsystem checks passed/failed/pending  
5. **Residual risks** — explicit, with proposed mitigations or waivers  

## Agent behavior

- Never present agent synthesis as **certified** engineering sign-off  
- Prefer **questions** and **options** when domain physics or safety is uncertain  
- If the user is not the right expert, label the task **needs_domain_expert** with suggested role (structures, thermal, RF, safety, etc.)  

## Product direction

Favor UI/API patterns: review queues, electronic signatures later, immutable baseline snapshots—without blocking early PoCs on full workflow engines.

## References

- [AGENT.md](../../AGENT.md) — orchestration and roles  
- [docs/INFORMATION_ARCHITECTURE.md](../../docs/INFORMATION_ARCHITECTURE.md) — artifact graph  
