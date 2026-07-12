# Engineering Agents — Verification plan

Verification asks: *Did we build the software right against its shalls?*  
Validation (ConOps achievement) is in [validation.md](validation.md).  
Matrix: [matrix.md](matrix.md).

## Methods

- **Test** — executable regression and loop smoke
- **Analysis** — review of proposal/evidence schemas and layer boundaries (as needed)
- **Inspection** — review of stored run artifacts

## First-class verification cases

### `VC-ea-loop-2run`

| Field | Content |
|-------|---------|
| Which requirements | `EA-SW-SYS-010`, `EA-SW-SYS-020` |
| Means | CLI → scenario: Cycle 1 run → emit proposals → Cycle 2 run with proposals applied |
| Judge | `C-N-ge-1`, `C-proposals_emitted`, `C-result_delta`, `C-truth-gate` |
| Evidence | `E-run1`, `E-run2` |
| Relation | `verify(VC-ea-loop-2run, EA-SW-SYS-010)`, `verify(VC-ea-loop-2run, EA-SW-SYS-020)` |

This case also anchors the ConOps **minimum success** gate (see [validation.md](validation.md)).

### `VC-ea-pytest`

| Field | Content |
|-------|---------|
| Which requirements | `EA-SW-SUB-CLI-010`, `EA-SW-SUB-SCN-010`, `EA-SW-SUB-AGT-010`, `EA-SW-SUB-ENV-010`, `EA-SW-SUB-CORE-010` |
| Means | Development regression test suite |
| Judge | `C-pytest_green` |
| Evidence | `E-pytest` |
| Relation | `verify(VC-ea-pytest, …)` for each subsystem requirement above |

## Constraint-backed auto-verification stance

Do **not** use naive requirement_id → shell auto-binding.  
Use the **system graph + constrain + deterministic truth gate** pattern ([competitor_tradeoff.md](competitor_tradeoff.md)).

## Machine-readable

[model/verification_cases.yaml](model/verification_cases.yaml)
