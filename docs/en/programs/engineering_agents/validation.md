# Engineering Agents — Validation plan

Validation asks: *Did we build the right software for the ConOps?*  
Verification against shalls: [verification.md](verification.md).

## ConOps reference

See [conops.md](conops.md): L1↔L2 for operator-set N → Final Design or Plan Change; truth via deterministic sim / constraints / evidence; human intervention allowed but time-costly.

## Minimum success (initial validation gate)

| Step | Expected |
|------|----------|
| Cycle 1 | L1↔L2 runs (N ≥ 1); non-empty design/parameter proposal emitted |
| Cycle 2 | Proposal applied; re-run yields **different results** vs Cycle 1 |

Mapped to verification case `VC-ea-loop-2run` (software), which `verify`s `EA-SW-SYS-010` and `EA-SW-SYS-020`.

## Broader validation intent

- Operators can run the loop via CLI with controllable N and proposal apply (`EA-SW-OPS-010`).
- Truth-seeking path does not accept LLM-only pass (`EA-SW-SYS-020`, `C-truth-gate`).
- Domain/plant outcomes are scenario content, not substitutes for software ConOps validation.
