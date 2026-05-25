import type { SsotActorKind } from "@one-piece/domain";

const LABELS: Record<SsotActorKind, string> = {
  human_engineer: "Human engineer",
  logic_automation: "Logic automation",
  ai_agent: "AI agent",
};

export function ActorBadge({
  kind,
  aiWarning,
}: {
  kind: SsotActorKind;
  aiWarning?: boolean;
}) {
  return (
    <span
      className={`actor-badge actor-${kind}${aiWarning ? " actor-ai-warning" : ""}`}
      title={
        aiWarning
          ? "AI touched a human-dominated artifact — verify before trusting"
          : undefined
      }
    >
      {LABELS[kind]}
      {aiWarning && <span className="ai-warning-mark" aria-label="AI touch warning"> ⚠</span>}
    </span>
  );
}
