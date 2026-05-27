import { useEffect, useMemo, useState } from "react";
import type {
  CoDesignRun,
  EngineeringGraph,
  EntityId,
  SsotProvenanceRecord,
} from "@one-piece/domain";
import type { SsotNodeKind } from "../lib/graph";
import { ActorBadge } from "./ActorBadge";
import { SsotGraphView } from "./SsotGraphView";

interface CoDesignViewProps {
  run?: CoDesignRun;
  model: EngineeringGraph;
  provenanceRecords: SsotProvenanceRecord[];
  selectedGraphNodeId: EntityId | null;
  selectedIterationId: EntityId | null;
  autonomousMode: boolean;
  reviewBypassed: boolean;
  onSelectGraphNode: (kind: SsotNodeKind, id: EntityId) => void;
  onSelectIteration: (id: EntityId) => void;
  onStartRun: (goal: string, maxIterations: number) => void;
  onStopRun: () => void;
}

function formatMetric(value: number, unit?: string) {
  return `${value.toFixed(3).replace(/\.?0+$/, "")}${unit ? ` ${unit}` : ""}`;
}

export function CoDesignView({
  run,
  model,
  provenanceRecords,
  selectedGraphNodeId,
  selectedIterationId,
  autonomousMode,
  reviewBypassed,
  onSelectGraphNode,
  onSelectIteration,
  onStartRun,
  onStopRun,
}: CoDesignViewProps) {
  const [goalInput, setGoalInput] = useState(run?.goal.objective ?? "");
  const [maxIterations, setMaxIterations] = useState(run?.goal.maxIterations ?? 5);

  useEffect(() => {
    if (!run) return;
    setGoalInput(run.goal.objective);
    setMaxIterations(run.goal.maxIterations);
  }, [run]);

  const selectedIteration = useMemo(() => {
    if (!run) return undefined;
    const fallback = run.iterations.at(-1);
    return (
      run.iterations.find((iteration) => iteration.id === selectedIterationId) ?? fallback
    );
  }, [run, selectedIterationId]);
  const initialIteration = run?.iterations[0];
  const finalIteration = run?.iterations.at(-1);

  const runActorBadge = autonomousMode ? "ai_agent" : "human_engineer";

  return (
    <div className="codesign-view">
      <header className="panel-header">
        <h2>Autonomous Co-Design</h2>
        <p className="panel-subtitle">
          Goal-driven loop: requirements evaluation, design-parameter mutation, and
          analysis evidence replay.
        </p>
      </header>

      <div className="codesign-toolbar">
        <section className="codesign-card">
          <div className="codesign-card-header">
            <div>
              <h3>Run control</h3>
              <p className="hint">
                Slide AI scope to 100% for autonomous mode. Below that, the same loop
                leaves artifacts for human review.
              </p>
            </div>
            <ActorBadge kind={runActorBadge} aiWarning={autonomousMode} />
          </div>

          <label className="field-label codesign-label" htmlFor="codesign-goal">
            Goal
          </label>
          <textarea
            id="codesign-goal"
            className="codesign-textarea"
            value={goalInput}
            onChange={(e) => setGoalInput(e.target.value)}
            rows={3}
          />

          <label className="field-label codesign-label" htmlFor="codesign-max-iterations">
            Max iterations
          </label>
          <input
            id="codesign-max-iterations"
            className="codesign-number"
            type="number"
            min={1}
            max={200}
            value={maxIterations}
            onChange={(e) => setMaxIterations(Number(e.target.value) || 1)}
          />

          <div className="lifecycle-actions">
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => onStartRun(goalInput, maxIterations)}
              disabled={!run}
            >
              Start run
            </button>
            <button type="button" className="btn btn-ghost" onClick={onStopRun}>
              Stop
            </button>
          </div>
        </section>

        <section className="codesign-card">
          <div className="codesign-card-header">
            <div>
              <h3>Mode</h3>
              <p className="hint">
                Autonomous mode bypasses the review queue for the active run, but still
                leaves full provenance and simulation evidence.
              </p>
            </div>
            <span
              className={`run-status ${
                autonomousMode ? "run-status-success" : "run-status-pending"
              }`}
            >
              {autonomousMode ? "AI 100%" : "human gated"}
            </span>
          </div>
          <dl className="meta-grid">
            <dt>Queue behavior</dt>
            <dd>{reviewBypassed ? "Bypassed during run" : "Human review required"}</dd>
            <dt>Run status</dt>
            <dd>{run?.status ?? "—"}</dd>
            <dt>Latest summary</dt>
            <dd>{run?.latestSummary ?? "No co-design run loaded."}</dd>
          </dl>
        </section>
      </div>

      {run ? (
        <div className="codesign-layout">
          <aside className="codesign-sidebar">
            <section className="codesign-card">
              <div className="codesign-card-header">
                <div>
                  <h3>Goal targets</h3>
                  <p className="hint">{run.goal.title}</p>
                </div>
              </div>
              <ul className="chip-list">
                {run.goal.targetMetrics.map((metric) => (
                  <li key={metric.key} className="chip">
                    {metric.label}: {metric.direction}
                    {metric.targetValue != null &&
                      ` ${formatMetric(metric.targetValue, metric.unit)}`}
                  </li>
                ))}
              </ul>
            </section>

            <section className="codesign-card">
              <div className="codesign-card-header">
                <div>
                  <h3>Run summary</h3>
                  <p className="hint">
                    Initial vs final metrics and iteration count for the active replay.
                  </p>
                </div>
              </div>
              {initialIteration && finalIteration ? (
                <div className="codesign-summary-list">
                  {finalIteration.metrics.map((metric) => {
                    const start = initialIteration.metrics.find((item) => item.key === metric.key);
                    return (
                      <div key={metric.key} className="codesign-summary-row">
                        <span className="graph-node-label">{metric.label}</span>
                        <strong>
                          {start ? formatMetric(start.value, start.unit) : "—"} →{" "}
                          {formatMetric(metric.value, metric.unit)}
                        </strong>
                      </div>
                    );
                  })}
                  <div className="codesign-summary-row">
                    <span className="graph-node-label">Iterations</span>
                    <strong>{run.iterations.length}</strong>
                  </div>
                  <div className="codesign-summary-row">
                    <span className="graph-node-label">Run status</span>
                    <strong>{run.status}</strong>
                  </div>
                </div>
              ) : (
                <p className="empty-state">Run summary will appear once iterations exist.</p>
              )}
            </section>

            <section className="codesign-card">
              <div className="codesign-card-header">
                <div>
                  <h3>Iteration timeline</h3>
                  <p className="hint">
                    Each iteration captures AI mutations, requirement checks, and
                    deterministic analysis output.
                  </p>
                </div>
              </div>
              <ul className="codesign-timeline">
                {run.iterations.map((iteration) => (
                  <li key={iteration.id}>
                    <button
                      type="button"
                      className={`codesign-iteration ${
                        selectedIteration?.id === iteration.id ? "selected" : ""
                      }`}
                      onClick={() => onSelectIteration(iteration.id)}
                    >
                      <span className="req-key">iter {iteration.index}</span>
                      <span>{iteration.summary}</span>
                      <span className="codesign-score">
                        score {iteration.objectiveScore.toFixed(2)}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          </aside>

          <div className="codesign-main">
            <section className="codesign-card">
              <div className="codesign-card-header">
                <div>
                  <h3>Selected iteration</h3>
                  <p className="hint">
                    Metrics and mutations below drive the live graph on the same page.
                  </p>
                </div>
                {selectedIteration && (
                  <span className="run-time">
                    {selectedIteration.startedAt} → {selectedIteration.completedAt}
                  </span>
                )}
              </div>

              {selectedIteration ? (
                <>
                  <div className="codesign-metric-grid">
                    {selectedIteration.metrics.map((metric) => (
                      <div key={metric.key} className="codesign-metric">
                        <span className="graph-node-label">{metric.label}</span>
                        <strong>{formatMetric(metric.value, metric.unit)}</strong>
                        {metric.status && (
                          <span className={`matrix-cell status-${statusClass(metric.status)}`}>
                            {metric.status}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="codesign-columns">
                    <section className="detail-block">
                      <h3>Mutations</h3>
                      <ul className="provenance-list">
                        {selectedIteration.mutations.map((mutation, index) => (
                          <li key={`${mutation.nodeId}-${index}`} className="provenance-row">
                            <p className="provenance-change">
                              <span className="req-key">{mutation.nodeKey}</span>{" "}
                              {mutation.fieldPath}:{" "}
                              {mutation.previousValue != null && (
                                <>
                                  <span className="value-old">{mutation.previousValue}</span> →{" "}
                                </>
                              )}
                              <span className="value-new">{mutation.newValue}</span>
                            </p>
                            {mutation.rationale && (
                              <p className="provenance-rationale">{mutation.rationale}</p>
                            )}
                          </li>
                        ))}
                      </ul>
                    </section>

                    <section className="detail-block">
                      <h3>Requirement checks</h3>
                      <ul className="provenance-list">
                        {selectedIteration.requirementChecks.map((check) => (
                          <li key={check.requirementId} className="provenance-row">
                            <p className="provenance-change">
                              <span className="req-key">{check.requirementKey}</span>{" "}
                              <span className={`matrix-cell status-${statusClass(check.status)}`}>
                                {check.status}
                              </span>
                            </p>
                            {check.note && (
                              <p className="provenance-rationale">{check.note}</p>
                            )}
                          </li>
                        ))}
                      </ul>
                    </section>
                  </div>

                  {selectedIteration.generatedProvenanceRecords &&
                    selectedIteration.generatedProvenanceRecords.length > 0 && (
                      <section className="detail-block">
                        <h3>Generated provenance</h3>
                        <ul className="provenance-list">
                          {selectedIteration.generatedProvenanceRecords.map((record) => (
                            <li key={record.id} className="provenance-row provenance-ai-touch">
                              <div className="provenance-meta">
                                <ActorBadge
                                  kind={record.actorKind}
                                  aiWarning={record.aiTouchInHumanDomain}
                                />
                                <span className="provenance-time">{record.occurredAt}</span>
                                <span className="provenance-actor">{record.actorLabel}</span>
                              </div>
                              <p className="provenance-change">
                                <span className="req-key">{record.nodeKey}</span>{" "}
                                {record.fieldPath}:{" "}
                                {record.previousValue != null && (
                                  <>
                                    <span className="value-old">{record.previousValue}</span> →{" "}
                                  </>
                                )}
                                <span className="value-new">{record.newValue}</span>
                              </p>
                              {record.rationale && (
                                <p className="provenance-rationale">{record.rationale}</p>
                              )}
                            </li>
                          ))}
                        </ul>
                      </section>
                    )}
                </>
              ) : (
                <p className="empty-state">No iteration selected.</p>
              )}
            </section>

            <section className="codesign-card codesign-graph-card">
              <div className="codesign-card-header">
                <div>
                  <h3>Live SSOT graph</h3>
                  <p className="hint">
                    This graph reflects the current program state as the run applies each
                    iteration.
                  </p>
                </div>
              </div>
              <div className="codesign-graph">
                <SsotGraphView
                  model={model}
                  selectedId={selectedGraphNodeId}
                  onSelect={onSelectGraphNode}
                />
              </div>
            </section>

            <section className="codesign-card">
              <div className="codesign-card-header">
                <div>
                  <h3>Live provenance tail</h3>
                  <p className="hint">Newest SSOT mutations from the current replay.</p>
                </div>
              </div>
              <ul className="provenance-list">
                {provenanceRecords
                  .slice()
                  .sort((a, b) => b.occurredAt.localeCompare(a.occurredAt))
                  .slice(0, 6)
                  .map((record) => (
                    <li
                      key={record.id}
                      className={`provenance-row${
                        record.aiTouchInHumanDomain ? " provenance-ai-touch" : ""
                      }`}
                    >
                      <div className="provenance-meta">
                        <ActorBadge
                          kind={record.actorKind}
                          aiWarning={record.aiTouchInHumanDomain}
                        />
                        <span className="provenance-time">{record.occurredAt}</span>
                        <span className="provenance-actor">{record.actorLabel}</span>
                      </div>
                      <p className="provenance-change">
                        <span className="req-key">{record.nodeKey}</span> {record.fieldPath}:{" "}
                        {record.previousValue != null && (
                          <>
                            <span className="value-old">{record.previousValue}</span> →{" "}
                          </>
                        )}
                        <span className="value-new">{record.newValue}</span>
                      </p>
                    </li>
                  ))}
              </ul>
            </section>
          </div>
        </div>
      ) : (
        <p className="empty-state">No co-design template is available.</p>
      )}
    </div>
  );
}

function statusClass(status: string): string {
  switch (status) {
    case "met":
    case "pass":
    case "improved":
      return "pass";
    case "regressed":
    case "fail":
    case "blocked":
      return "fail";
    case "improving":
      return "planned";
    case "unmet":
      return "gap";
    default:
      return "planned";
  }
}
