import type { EntityId, LifecycleState, Requirement, SystemElement } from "@one-piece/domain";
import { StateBadge } from "./StateBadge";

interface RequirementDetailProps {
  requirement: Requirement;
  element?: SystemElement;
  onAdvanceLifecycle: (id: EntityId, next: LifecycleState) => void;
}

export function RequirementDetail({
  requirement,
  element,
  onAdvanceLifecycle,
}: RequirementDetailProps) {
  const { id, state } = requirement;

  return (
    <section className="detail-section">
      <header className="detail-header">
        <div>
          <p className="detail-level">
            {requirement.level} · {requirement.kind.replace("_", " ")}
          </p>
          <h1>
            <span className="req-key">{requirement.key}</span> {requirement.title}
          </h1>
        </div>
        <StateBadge state={state} />
      </header>

      <p className="statement">{requirement.statement}</p>

      {requirement.rationale && (
        <div className="detail-block">
          <h3>Rationale</h3>
          <p>{requirement.rationale}</p>
        </div>
      )}

      <dl className="meta-grid">
        {requirement.owner && (
          <>
            <dt>Owner</dt>
            <dd>{requirement.owner}</dd>
          </>
        )}
        {element && (
          <>
            <dt>System</dt>
            <dd>{element.name}</dd>
          </>
        )}
      </dl>

      <div className="lifecycle-actions">
        {state === "draft" && (
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => onAdvanceLifecycle(id, "under_review")}
          >
            Submit for review
          </button>
        )}
        {state === "under_review" && (
          <>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => onAdvanceLifecycle(id, "baseline")}
            >
              Baseline
            </button>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => onAdvanceLifecycle(id, "draft")}
            >
              Return to draft
            </button>
          </>
        )}
      </div>
    </section>
  );
}
