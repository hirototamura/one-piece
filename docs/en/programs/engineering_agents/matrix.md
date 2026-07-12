# Engineering Agents — Compliance matrix (draft)

Requirement × verification case. Evidence columns filled when runs/tests are recorded.

| Requirement | VC-ea-loop-2run | VC-ea-pytest | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| `EA-SW-MIS-001` | (via SYS) | — | planned | — |
| `EA-SW-SYS-010` | verify | — | planned | E-run1, E-run2 |
| `EA-SW-SYS-020` | verify | — | planned | E-run1, E-run2 |
| `EA-SW-OPS-010` | (exercised by means) | — | planned | E-run1, E-run2 |
| `EA-SW-OPS-020` | — | — | planned | (intervention path; not automated) |
| `EA-SW-SUB-CLI-010` | — | verify | planned | E-pytest |
| `EA-SW-SUB-SCN-010` | — | verify | planned | E-pytest |
| `EA-SW-SUB-AGT-010` | — | verify | planned | E-pytest |
| `EA-SW-SUB-ENV-010` | — | verify | planned | E-pytest |
| `EA-SW-SUB-CORE-010` | — | verify | planned | E-pytest |

Relations use verb base forms: `verify(verification_case, requirement)`.  
Full graph: [system_graph.md](system_graph.md).
