import type {
  DesignConstraint,
  EntityId,
  LifecycleState,
  Requirement,
} from "@one-piece/domain";
import { StateBadge } from "./StateBadge";
import type { SsotNodeKind } from "../lib/graph";

type ReviewItem =
  | { kind: "requirement"; item: Requirement }
  | { kind: "constraint"; item: DesignConstraint };

interface ReviewQueueProps {
  requirements: Requirement[];
  constraints: DesignConstraint[];
  bypassed?: boolean;
  selectedId: EntityId | null;
  onSelect: (id: EntityId, kind: SsotNodeKind) => void;
  onAdvanceRequirement: (id: EntityId, next: LifecycleState) => void;
  onAdvanceConstraint: (id: EntityId, next: LifecycleState) => void;
}

export function ReviewQueue({
  requirements,
  constraints,
  bypassed = false,
  selectedId,
  onSelect,
  onAdvanceRequirement,
  onAdvanceConstraint,
}: ReviewQueueProps) {
  const items: ReviewItem[] = [
    ...requirements
      .filter((r) => r.state === "draft" || r.state === "under_review")
      .map((item) => ({ kind: "requirement" as const, item })),
    ...constraints
      .filter((c) => c.state === "draft" || c.state === "under_review")
      .map((item) => ({ kind: "constraint" as const, item })),
  ];

  const selected = items.find((x) => x.item.id === selectedId);

  return (
    <div className="split-view review-view">
      <aside className="panel panel-list">
        <header className="panel-header">
          <h2>Review queue</h2>
          <p className="panel-subtitle">
            {bypassed
              ? "Autonomous co-design is active — this queue is temporarily bypassed."
              : "Human gate — baseline after review (agents draft only)."}
          </p>
        </header>
        {bypassed ? (
          <p className="empty-state">
            Review is bypassed while the autonomous run is active. Provenance is still
            recorded for later inspection.
          </p>
        ) : items.length === 0 ? (
          <p className="empty-state">Nothing awaiting review.</p>
        ) : (
          <ul className="review-list">
            {items.map(({ kind, item }) => (
              <li key={item.id}>
                <button
                  type="button"
                  className={`review-row ${selectedId === item.id ? "selected" : ""}`}
                  onClick={() => onSelect(item.id, kind)}
                >
                  <span className="node-kind">{kind}</span>
                  <span className="req-key">{item.key}</span>
                  <span>{item.title}</span>
                  <StateBadge state={item.state} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </aside>
      <div className="panel panel-detail">
        {selected ? (
          <>
            <p className="statement">{selected.item.statement}</p>
            <div className="lifecycle-actions">
              {selected.item.state === "draft" && (
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() =>
                    selected.kind === "requirement"
                      ? onAdvanceRequirement(selected.item.id, "under_review")
                      : onAdvanceConstraint(selected.item.id, "under_review")
                  }
                >
                  Submit for review
                </button>
              )}
              {selected.item.state === "under_review" && (
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() =>
                    selected.kind === "requirement"
                      ? onAdvanceRequirement(selected.item.id, "baseline")
                      : onAdvanceConstraint(selected.item.id, "baseline")
                  }
                >
                  Baseline
                </button>
              )}
            </div>
          </>
        ) : (
          <p className="empty-state">Select an item to review.</p>
        )}
      </div>
    </div>
  );
}
