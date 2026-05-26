import type {
  CellCodeBinding,
  DesignArtifact,
  EngineeringGraph,
  EntityId,
  IntegrationRun,
} from "@one-piece/domain";
import { ActorBadge } from "./ActorBadge";

interface DesignIntegrationViewProps {
  model: EngineeringGraph;
  integrationRuns: IntegrationRun[];
  selectedBindingId: EntityId | null;
  onSelectBinding: (id: EntityId) => void;
}

export function DesignIntegrationView({
  model,
  integrationRuns,
  selectedBindingId,
  onSelectBinding,
}: DesignIntegrationViewProps) {
  const artifacts = model.designArtifacts ?? [];
  const bindings = model.cellCodeBindings ?? [];

  const selected = bindings.find((b) => b.id === selectedBindingId);

  return (
    <div className="integration-view">
      <header className="panel-header">
        <div>
          <h2>Design integration</h2>
          <p className="panel-subtitle">
            Excel workbooks and Python scripts versioned in SSOT. Minimum unit: cell
            change → script sync → re-run (logic automation).
          </p>
        </div>
      </header>

      <div className="split-view integration-split">
        <aside className="panel panel-list">
          <h3>Registered artifacts</h3>
          <ul className="artifact-list">
            {artifacts.map((a) => (
              <ArtifactRow key={a.id} artifact={a} />
            ))}
          </ul>

          <h3>Cell ↔ code bindings</h3>
          <ul className="binding-list">
            {bindings.map((b) => (
              <li key={b.id}>
                <button
                  type="button"
                  className={`binding-item${selectedBindingId === b.id ? " active" : ""}`}
                  onClick={() => onSelectBinding(b.id)}
                >
                  <span className="mono">{b.excelCellRef}</span>
                  <span className="binding-arrow">→</span>
                  <span className="mono">{b.pythonMarker}</span>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <div className="panel panel-detail">
          {selected ? (
            <BindingDetail
              binding={selected}
              artifacts={artifacts}
              model={model}
            />
          ) : (
            <p className="empty-state">Select a binding to inspect sync path.</p>
          )}

          <section className="detail-block">
            <h3>Integration runs (logic automation)</h3>
            {integrationRuns.length === 0 ? (
              <p className="empty-state">No runs yet.</p>
            ) : (
              <ul className="run-list">
                {integrationRuns.map((run) => (
                  <li key={run.id} className={`run-row run-${run.status}`}>
                    <div className="run-meta">
                      <ActorBadge kind={run.triggeredBy} />
                      <span className="run-time">
                        {new Date(run.startedAt).toLocaleString()}
                      </span>
                      <span className={`run-status run-status-${run.status}`}>
                        {run.status}
                      </span>
                    </div>
                    {run.outputSummary && (
                      <pre className="run-output">{run.outputSummary}</pre>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

function ArtifactRow({ artifact }: { artifact: DesignArtifact }) {
  return (
    <li className="artifact-row">
      <span className={`artifact-kind kind-${artifact.kind}`}>
        {artifact.kind === "excel_workbook" ? "XLS" : "PY"}
      </span>
      <div>
        <span className="req-key">{artifact.key}</span> {artifact.name}
        <p className="artifact-path mono">{artifact.sourcePath}</p>
      </div>
    </li>
  );
}

function BindingDetail({
  binding,
  artifacts,
  model,
}: {
  binding: CellCodeBinding;
  artifacts: DesignArtifact[];
  model: EngineeringGraph;
}) {
  const excel = artifacts.find((a) => a.id === binding.excelArtifactId);
  const python = artifacts.find((a) => a.id === binding.pythonArtifactId);
  const param = model.designParameters.find(
    (p) => p.id === binding.designParameterId,
  );

  return (
    <section className="detail-block">
      <h3>Binding detail</h3>
      <dl className="meta-grid">
        <dt>Excel cell</dt>
        <dd className="mono">{binding.excelCellRef}</dd>
        <dt>Workbook</dt>
        <dd>{excel?.name ?? binding.excelArtifactId}</dd>
        <dt>Python marker</dt>
        <dd className="mono">{binding.pythonMarker}</dd>
        {binding.pythonAssignmentName && (
          <>
            <dt>Executable variable</dt>
            <dd className="mono">{binding.pythonAssignmentName}</dd>
          </>
        )}
        <dt>Script</dt>
        <dd>{python?.name ?? binding.pythonArtifactId}</dd>
        <dt>SSOT parameter</dt>
        <dd>
          {param ? (
            <>
              <span className="req-key">{param.key}</span> {param.name} ={" "}
              {String(param.value)}
              {param.unit ? ` ${param.unit}` : ""}
            </>
          ) : (
            binding.designParameterId
          )}
        </dd>
      </dl>
      <p className="hint">
        When the Excel cell changes, logic automation updates the Python marker and
        re-executes the script — no AI in this loop.
      </p>
    </section>
  );
}
