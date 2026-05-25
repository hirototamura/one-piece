import type { EngineeringGraph, EntityId, SsotProvenanceRecord } from "@one-piece/domain";
import { ProvenancePanel } from "./AgentPolicyView";
import { GraphLinksPanel } from "./GraphLinksPanel";
import { StateBadge } from "./StateBadge";
import type { SsotNodeKind } from "../lib/graph";

interface DesignViewProps {
  model: EngineeringGraph;
  provenanceRecords: SsotProvenanceRecord[];
  tab: "parameters" | "constraints";
  onTabChange: (tab: "parameters" | "constraints") => void;
  selectedId: EntityId | null;
  onSelect: (id: EntityId) => void;
  onNavigate: (kind: SsotNodeKind, id: EntityId) => void;
}

export function DesignView({
  model,
  provenanceRecords,
  tab,
  onTabChange,
  selectedId,
  onSelect,
  onNavigate,
}: DesignViewProps) {
  const params = model.designParameters;
  const constraints = model.designConstraints;

  const selectedParam = params.find((p) => p.id === selectedId);
  const selectedConstraint = constraints.find((c) => c.id === selectedId);

  return (
    <div className="split-view">
      <aside className="panel panel-list">
        <header className="panel-header">
          <h2>Design</h2>
          <div className="level-tabs">
            <button
              type="button"
              className={tab === "parameters" ? "active" : ""}
              onClick={() => onTabChange("parameters")}
            >
              Parameters
            </button>
            <button
              type="button"
              className={tab === "constraints" ? "active" : ""}
              onClick={() => onTabChange("constraints")}
            >
              Constraints
            </button>
          </div>
        </header>
        <ul className="review-list">
          {tab === "parameters"
            ? params.map((p) => (
                <li key={p.id}>
                  <button
                    type="button"
                    className={`review-row ${selectedId === p.id ? "selected" : ""}`}
                    onClick={() => onSelect(p.id)}
                  >
                    <span className="req-key">{p.key}</span>
                    <span>
                      {p.name} = {String(p.value)} {p.unit ?? ""}
                    </span>
                    <StateBadge state={p.state} />
                  </button>
                </li>
              ))
            : constraints.map((c) => (
                <li key={c.id}>
                  <button
                    type="button"
                    className={`review-row ${selectedId === c.id ? "selected" : ""}`}
                    onClick={() => onSelect(c.id)}
                  >
                    <span className="req-key">{c.key}</span>
                    <span>{c.title}</span>
                    {c.actsAsFunctionalRequirement && (
                      <span className="tag tag-functional">V&amp;V</span>
                    )}
                    <StateBadge state={c.state} />
                  </button>
                </li>
              ))}
        </ul>
      </aside>
      <div className="panel panel-detail">
        {tab === "parameters" && selectedParam && (
          <>
            <section className="detail-section">
              <header className="detail-header">
                <div>
                  <p className="detail-level">{selectedParam.discipline}</p>
                  <h1>
                    <span className="req-key">{selectedParam.key}</span>{" "}
                    {selectedParam.name}
                  </h1>
                </div>
                <StateBadge state={selectedParam.state} />
              </header>
              <p className="statement">
                Value: <strong>{String(selectedParam.value)}</strong>
                {selectedParam.unit ? ` ${selectedParam.unit}` : ""}
              </p>
            </section>
            <ProvenancePanel
              records={provenanceRecords}
              nodeId={selectedParam.id}
            />
            <GraphLinksPanel
              model={model}
              nodeId={selectedParam.id}
              nodeKind="parameter"
              onNavigate={onNavigate}
            />
          </>
        )}
        {tab === "constraints" && selectedConstraint && (
          <>
            <section className="detail-section">
              <header className="detail-header">
                <div>
                  <p className="detail-level">
                    Design constraint
                    {selectedConstraint.actsAsFunctionalRequirement &&
                      " · acts as functional requirement"}
                  </p>
                  <h1>
                    <span className="req-key">{selectedConstraint.key}</span>{" "}
                    {selectedConstraint.title}
                  </h1>
                </div>
                <StateBadge state={selectedConstraint.state} />
              </header>
              <p className="statement">{selectedConstraint.statement}</p>
              {selectedConstraint.actsAsFunctionalRequirement && (
                <p className="tag-line">
                  <span className="tag tag-functional">
                    Included in verification closure
                  </span>
                </p>
              )}
            </section>
            <GraphLinksPanel
              model={model}
              nodeId={selectedConstraint.id}
              nodeKind="constraint"
              onNavigate={onNavigate}
            />
          </>
        )}
        {((tab === "parameters" && !selectedParam) ||
          (tab === "constraints" && !selectedConstraint)) && (
          <p className="empty-state">Select an item.</p>
        )}
      </div>
    </div>
  );
}
