# one-piece

Systems engineering SaaS proof of concept for hardware products—requirements, architecture, interfaces, verification, and agent-assisted workflows. Built for **teams of any size**; **small teams first** on the roadmap, with scale-specific touchpoints to follow.

## Agent orchestration & docs

| Path | Purpose |
|------|---------|
| [AGENT.md](./AGENT.md) | Multi-agent roles, workflows, human-in-the-loop gates |
| [docs/](./docs/) | Living plan, information architecture, progress log |

## Layout

| Path | Purpose |
|------|---------|
| `packages/domain` | Shared domain model (requirements, system elements, traceability) |
| `apps/` | Reserved for future API, workers, and human-facing clients |
| `.cursor/skills/` | Project skills for domain + human review workflows |

## Prerequisites

- Node.js 20+

## Commands

```bash
npm install
npm run build -w @one-piece/domain
```

## License

Proprietary / TBD.
