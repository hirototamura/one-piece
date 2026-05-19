import type { EngineeringGraph, EntityId } from "@one-piece/domain";
import { resolveNode, type SsotNodeKind } from "../lib/graph";

interface SsotGraphViewProps {
  model: EngineeringGraph;
  selectedId: EntityId | null;
  onSelect: (kind: SsotNodeKind, id: EntityId) => void;
}

const COLUMNS: { kind: SsotNodeKind; title: string }[] = [
  { kind: "element", title: "Elements" },
  { kind: "requirement", title: "Requirements" },
  { kind: "icd", title: "ICDs" },
  { kind: "parameter", title: "Parameters" },
  { kind: "constraint", title: "Constraints" },
  { kind: "cad", title: "CAD" },
];

function nodesForKind(model: EngineeringGraph, kind: SsotNodeKind) {
  switch (kind) {
    case "element":
      return model.elements.map((e) => ({
        id: e.id,
        key: e.kind,
        label: e.name,
      }));
    case "requirement":
      return model.requirements.map((r) => ({
        id: r.id,
        key: r.key,
        label: r.title,
      }));
    case "icd":
      return model.interfaceControlDocuments.map((i) => ({
        id: i.id,
        key: i.key,
        label: i.title,
      }));
    case "parameter":
      return model.designParameters.map((p) => ({
        id: p.id,
        key: p.key,
        label: p.name,
      }));
    case "constraint":
      return model.designConstraints.map((c) => ({
        id: c.id,
        key: c.key,
        label: c.title,
      }));
    case "cad":
      return model.cadModels.map((c) => ({
        id: c.id,
        key: c.key,
        label: c.name,
      }));
  }
}

export function SsotGraphView({
  model,
  selectedId,
  onSelect,
}: SsotGraphViewProps) {
  return (
    <div className="graph-view">
      <header className="panel-header graph-header">
        <h2>SSOT graph</h2>
        <p className="panel-subtitle">
          Normalized program graph — click a node, then inspect links in detail views.
        </p>
      </header>
      <div className="graph-columns">
        {COLUMNS.map((col) => (
          <div key={col.kind} className="graph-column">
            <h3>{col.title}</h3>
            <ul>
              {nodesForKind(model, col.kind).map((n) => (
                <li key={n.id}>
                  <button
                    type="button"
                    className={`graph-node ${selectedId === n.id ? "selected" : ""}`}
                    onClick={() => onSelect(col.kind, n.id)}
                  >
                    <span className="req-key">{n.key}</span>
                    <span className="graph-node-label">{n.label}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <section className="graph-edges">
        <h3>Trace edges ({model.traces.length})</h3>
        <ul className="edge-list">
          {model.traces.map((t) => {
            const src = resolveNode(model, t.sourceId);
            const tgt = resolveNode(model, t.targetId);
            if (!src || !tgt) return null;
            return (
              <li key={t.id}>
                <button
                  type="button"
                  className="link-button"
                  onClick={() => onSelect(src.kind, src.id)}
                >
                  {src.key}
                </button>
                <span className="trace-relation">{t.relation}</span>
                <button
                  type="button"
                  className="link-button"
                  onClick={() => onSelect(tgt.kind, tgt.id)}
                >
                  {tgt.key}
                </button>
              </li>
            );
          })}
        </ul>
      </section>
    </div>
  );
}
