import type {
  EngineeringGraph,
  EntityId,
  InterfaceControlDocument,
} from "@one-piece/domain";
import { linkedParametersForIcd } from "../lib/graph";
import { GraphLinksPanel } from "./GraphLinksPanel";
import { StateBadge } from "./StateBadge";
import type { SsotNodeKind } from "../lib/graph";

interface InterfaceViewProps {
  model: EngineeringGraph;
  selectedId: EntityId | null;
  onSelect: (id: EntityId) => void;
  onNavigate: (kind: SsotNodeKind, id: EntityId) => void;
}

function IcdDetail({
  icd,
  model,
  onNavigate,
}: {
  icd: InterfaceControlDocument;
  model: EngineeringGraph;
  onNavigate: (kind: SsotNodeKind, id: EntityId) => void;
}) {
  const provider = model.elements.find((e) => e.id === icd.providerElementId);
  const consumer = model.elements.find((e) => e.id === icd.consumerElementId);
  const ifParams = model.interfaceParameters.filter((p) => p.icdId === icd.id);
  const designParams = linkedParametersForIcd(model, icd.id);

  return (
    <div className="panel panel-detail">
      <section className="detail-section">
        <header className="detail-header">
          <div>
            <p className="detail-level">Interface Control Document</p>
            <h1>
              <span className="req-key">{icd.key}</span> {icd.title}
            </h1>
          </div>
          <StateBadge state={icd.state} />
        </header>
        <p className="statement">{icd.scope}</p>
        <dl className="meta-grid">
          <dt>Provider</dt>
          <dd>{provider?.name ?? icd.providerElementId}</dd>
          <dt>Consumer</dt>
          <dd>{consumer?.name ?? icd.consumerElementId}</dd>
          {icd.disciplines && (
            <>
              <dt>Disciplines</dt>
              <dd>{icd.disciplines.join(", ")}</dd>
            </>
          )}
        </dl>

        <div className="detail-block">
          <h3>Interface parameters</h3>
          {ifParams.length === 0 ? (
            <p className="muted">None defined.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Dir</th>
                  <th>Range</th>
                  <th>Design param</th>
                </tr>
              </thead>
              <tbody>
                {ifParams.map((p) => (
                  <tr key={p.id}>
                    <td>{p.name}</td>
                    <td>{p.direction}</td>
                    <td>
                      {p.min != null && p.max != null
                        ? `${p.min}–${p.max} ${p.unit ?? ""}`
                        : (p.nominal ?? "—")}
                    </td>
                    <td>
                      {p.designParameterId ? (
                        <button
                          type="button"
                          className="link-button"
                          onClick={() =>
                            onNavigate("parameter", p.designParameterId!)
                          }
                        >
                          {designParams.find((d) => d.id === p.designParameterId)
                            ?.key ?? p.designParameterId}
                        </button>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
      <GraphLinksPanel
        model={model}
        nodeId={icd.id}
        nodeKind="icd"
        onNavigate={onNavigate}
      />
    </div>
  );
}

export function InterfaceView({
  model,
  selectedId,
  onSelect,
  onNavigate,
}: InterfaceViewProps) {
  const selected = model.interfaceControlDocuments.find(
    (i) => i.id === selectedId,
  );

  return (
    <div className="split-view">
      <aside className="panel panel-list">
        <header className="panel-header">
          <h2>Interfaces (ICD)</h2>
          <p className="panel-subtitle">
            Subsystem interface agreements in SSOT — provider ↔ consumer.
          </p>
        </header>
        <ul className="review-list">
          {model.interfaceControlDocuments.map((icd) => (
            <li key={icd.id}>
              <button
                type="button"
                className={`review-row ${selectedId === icd.id ? "selected" : ""}`}
                onClick={() => onSelect(icd.id)}
              >
                <span className="req-key">{icd.key}</span>
                <span>{icd.title}</span>
                <StateBadge state={icd.state} />
              </button>
            </li>
          ))}
        </ul>
      </aside>
      {selected ? (
        <IcdDetail icd={selected} model={model} onNavigate={onNavigate} />
      ) : (
        <div className="panel panel-detail">
          <p className="empty-state">Select an ICD.</p>
        </div>
      )}
    </div>
  );
}
