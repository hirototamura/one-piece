import type { CadModel, EngineeringGraph, EntityId } from "@one-piece/domain";
import { GraphLinksPanel } from "./GraphLinksPanel";
import type { SsotNodeKind } from "../lib/graph";

interface CadViewProps {
  model: EngineeringGraph;
  selectedId: EntityId | null;
  onSelect: (id: EntityId) => void;
  onNavigate: (kind: SsotNodeKind, id: EntityId) => void;
}

function SyncBadge({ status }: { status: CadModel["syncStatus"] }) {
  return <span className={`sync-badge sync-${status}`}>{status}</span>;
}

export function CadView({
  model,
  selectedId,
  onSelect,
  onNavigate,
}: CadViewProps) {
  const selected = model.cadModels.find((c) => c.id === selectedId);

  return (
    <div className="split-view">
      <aside className="panel panel-list">
        <header className="panel-header">
          <h2>CAD models</h2>
          <p className="panel-subtitle">
            SSOT nodes — live sync from PLM/CAD on every design change.
          </p>
        </header>
        <ul className="review-list">
          {model.cadModels.map((cad) => (
            <li key={cad.id}>
              <button
                type="button"
                className={`review-row ${selectedId === cad.id ? "selected" : ""}`}
                onClick={() => onSelect(cad.id)}
              >
                <span className="req-key">{cad.key}</span>
                <span>{cad.name}</span>
                <SyncBadge status={cad.syncStatus} />
              </button>
            </li>
          ))}
        </ul>
      </aside>
      <div className="panel panel-detail">
        {selected ? (
          <>
            <section className="detail-section">
              <header className="detail-header">
                <div>
                  <p className="detail-level">{selected.discipline} · CAD</p>
                  <h1>
                    <span className="req-key">{selected.key}</span> {selected.name}
                  </h1>
                </div>
                <SyncBadge status={selected.syncStatus} />
              </header>
              <dl className="meta-grid">
                <dt>Revision</dt>
                <dd>{selected.revision}</dd>
                <dt>Last synced</dt>
                <dd>{new Date(selected.lastSyncedAt).toLocaleString()}</dd>
                <dt>Source</dt>
                <dd className="mono-uri">{selected.sourceUri}</dd>
                {selected.checksum && (
                  <>
                    <dt>Checksum</dt>
                    <dd className="mono-uri">{selected.checksum}</dd>
                  </>
                )}
                <dt>Element</dt>
                <dd>
                  {model.elements.find((e) => e.id === selected.elementId)?.name ??
                    selected.elementId}
                </dd>
              </dl>
              {selected.extractedParameterIds &&
                selected.extractedParameterIds.length > 0 && (
                  <div className="detail-block">
                    <h3>Extracted parameters</h3>
                    <ul className="chip-list">
                      {selected.extractedParameterIds.map((pid) => {
                        const p = model.designParameters.find((x) => x.id === pid);
                        return (
                          <li key={pid}>
                            <button
                              type="button"
                              className="chip link-button"
                              onClick={() => onNavigate("parameter", pid)}
                            >
                              {p?.key ?? pid}
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
            </section>
            <GraphLinksPanel
              model={model}
              nodeId={selected.id}
              nodeKind="cad"
              onNavigate={onNavigate}
            />
          </>
        ) : (
          <p className="empty-state">Select a CAD model.</p>
        )}
      </div>
    </div>
  );
}
