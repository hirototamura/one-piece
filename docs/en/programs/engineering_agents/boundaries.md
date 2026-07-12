# Engineering Agents — Boundaries

Software boundaries (interfaces between EA subsystems and to the external sim backend).  
Machine-readable: [model/boundaries.yaml](model/boundaries.yaml).

| ID | From | To | Notes |
|----|------|-----|-------|
| `B-cli-scenario` | CLI / tools | scenario | Operator entry; run control |
| `B-scenario-agents` | scenario | agents | Team invocation, shared context |
| `B-scenario-env` | scenario | environment | Plant/backend stepping and telemetry pull |
| `B-scenario-core` | scenario | core | Shared state, proposals, results persistence |
| `B-env-backend` | environment | external sim / plant backend | Integration IF only—not domain requirements |

## Allocation

- `allocate(B-cli-scenario, EA-SW-SUB-CLI-010)`
- `allocate(B-scenario-agents, EA-SW-SUB-AGT-010)`
- `allocate(B-scenario-env, EA-SW-SUB-SCN-010)`
- `allocate(B-scenario-core, EA-SW-SUB-CORE-010)`
- `allocate(B-env-backend, EA-SW-SUB-ENV-010)`

See [system_model.md](system_model.md).
