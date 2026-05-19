import type { LifecycleState } from "@one-piece/domain";

const LABELS: Record<LifecycleState, string> = {
  draft: "Draft",
  under_review: "In review",
  baseline: "Baseline",
  obsolete: "Obsolete",
};

export function StateBadge({ state }: { state: LifecycleState }) {
  return <span className={`state-badge state-${state}`}>{LABELS[state]}</span>;
}
