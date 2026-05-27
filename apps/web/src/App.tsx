import { useEffect, useMemo, useRef, useState } from "react";
import type {
  AgentScopePolicy,
  CoDesignIteration,
  EntityId,
  IntegrationRun,
  LifecycleState,
  Program,
  Requirement,
  RequirementLevel,
} from "@one-piece/domain";
import {
  ALL_SSOT_MUTABLE_NODE_KINDS,
  aiTouchesInHumanDomain,
  isAutonomousCoDesign,
  shouldBypassHumanReview,
} from "@one-piece/domain";
import "./App.css";
import { createDemoProgram } from "./data/demoProgram";
import { AgentPolicyView, ProvenancePanel } from "./components/AgentPolicyView";
import { AppShell, type AppView } from "./components/AppShell";
import { CadView } from "./components/CadView";
import { CoDesignView } from "./components/CoDesignView";
import { ComplianceMatrix } from "./components/ComplianceMatrix";
import { DesignIntegrationView } from "./components/DesignIntegrationView";
import { DesignView } from "./components/DesignView";
import { GraphLinksPanel } from "./components/GraphLinksPanel";
import { InterfaceView } from "./components/InterfaceView";
import { RequirementDetail } from "./components/RequirementDetail";
import { RequirementsTree } from "./components/RequirementsTree";
import { ReviewQueue } from "./components/ReviewQueue";
import { SsotGraphView } from "./components/SsotGraphView";
import {
  getVerificationSubjects,
  linkedConstraintsForRequirement,
  type SsotNodeKind,
} from "./lib/graph";

const LEVEL_ORDER: RequirementLevel[] = [
  "mission",
  "system",
  "operational",
  "subsystem",
];

const CO_DESIGN_RUN_ID = "cdr-1";

export function App() {
  const [program, setProgram] = useState<Program>(() => createDemoProgram());
  const [view, setView] = useState<AppView>("coDesign");
  const [selection, setSelection] = useState<{
    kind: SsotNodeKind;
    id: EntityId;
  }>({ kind: "requirement", id: "req-s1" });
  const [designTab, setDesignTab] = useState<"parameters" | "constraints">(
    "parameters",
  );
  const [selectedBindingId, setSelectedBindingId] = useState<EntityId | null>(
    "bind-vbus",
  );
  const [levelFilter, setLevelFilter] = useState<RequirementLevel | "all">(
    "all",
  );
  const [selectedIterationId, setSelectedIterationId] = useState<EntityId | null>(
    null,
  );
  const runTimerRef = useRef<number | null>(null);

  const { model } = program;
  const selectedId = selection.id;
  const activeCoDesignRun =
    program.coDesignRuns.find((run) => run.id === CO_DESIGN_RUN_ID) ??
    program.coDesignRuns[0];
  const coDesignRunActive = activeCoDesignRun?.status === "running";
  const reviewBypassed = shouldBypassHumanReview(
    program.agentScopePolicy,
    coDesignRunActive,
  );

  const activeConfig = program.configurations.find(
    (c) => c.id === program.activeConfigurationId,
  );

  const requirements = useMemo(() => {
    const reqs = model.requirements;
    if (levelFilter === "all") return reqs;
    return reqs.filter((r) => r.level === levelFilter);
  }, [model.requirements, levelFilter]);

  const selectedRequirement: Requirement | undefined =
    selection.kind === "requirement"
      ? model.requirements.find((r) => r.id === selectedId)
      : undefined;

  const reviewItems = [
    ...model.requirements.filter(
      (r) => r.state === "draft" || r.state === "under_review",
    ),
    ...model.designConstraints.filter(
      (c) => c.state === "draft" || c.state === "under_review",
    ),
  ];

  const matrixSubjects = useMemo(() => {
    return getVerificationSubjects(model).filter((s) => {
      if (s.source !== "requirement") return true;
      const r = model.requirements.find((x) => x.id === s.id);
      return r?.level !== "mission";
    });
  }, [model]);

  const linkedConstraints = selectedRequirement
    ? linkedConstraintsForRequirement(model, selectedRequirement.id)
    : [];

  const aiWarningCount = aiTouchesInHumanDomain(program.provenanceRecords).length;
  const reviewCount = reviewBypassed ? 0 : reviewItems.length;

  useEffect(() => {
    return () => {
      if (runTimerRef.current != null) window.clearInterval(runTimerRef.current);
    };
  }, []);

  function setAgentScopePolicy(policy: AgentScopePolicy) {
    setProgram((p) => ({
      ...p,
      agentScopePolicy: {
        ...policy,
        autonomousCoDesign: policy.allowedFraction >= 1,
      },
    }));
  }

  function navigate(kind: SsotNodeKind, id: EntityId) {
    setSelection({ kind, id });
    switch (kind) {
      case "requirement":
        setView("requirements");
        break;
      case "icd":
        setView("interfaces");
        break;
      case "parameter":
        setView("design");
        setDesignTab("parameters");
        break;
      case "constraint":
        setView("design");
        setDesignTab("constraints");
        break;
      case "cad":
        setView("cad");
        break;
      default:
        setView("graph");
    }
  }

  function setActiveConfiguration(configId: EntityId) {
    setProgram((p) => ({ ...p, activeConfigurationId: configId }));
  }

  function advanceRequirementLifecycle(id: EntityId, next: LifecycleState) {
    setProgram((p) => ({
      ...p,
      model: {
        ...p.model,
        requirements: p.model.requirements.map((r) =>
          r.id === id ? { ...r, state: next } : r,
        ),
      },
    }));
  }

  function advanceConstraintLifecycle(id: EntityId, next: LifecycleState) {
    setProgram((p) => ({
      ...p,
      model: {
        ...p.model,
        designConstraints: p.model.designConstraints.map((c) =>
          c.id === id ? { ...c, state: next } : c,
        ),
      },
    }));
  }

  function stopCoDesignRun() {
    if (runTimerRef.current != null) {
      window.clearInterval(runTimerRef.current);
      runTimerRef.current = null;
    }
    setProgram((p) => ({
      ...p,
      coDesignRuns: p.coDesignRuns.map((run) =>
        run.id === activeCoDesignRun?.id && run.status === "running"
          ? {
              ...run,
              status: "stopped",
              completedAt: new Date().toISOString(),
              latestSummary: "Run stopped by operator.",
            }
          : run,
      ),
    }));
  }

  function startCoDesignRun(goal: string, maxIterations: number) {
    if (!activeCoDesignRun) return;
    if (runTimerRef.current != null) window.clearInterval(runTimerRef.current);

    const freshProgram = createDemoProgram();
    const baseRun = freshProgram.coDesignRuns.find((run) => run.id === activeCoDesignRun.id);
    if (!baseRun) return;

    const autonomousMode = isAutonomousCoDesign(program.agentScopePolicy);
    const policy = autonomousMode
      ? {
          ...program.agentScopePolicy,
          allowedNodeKinds: ALL_SSOT_MUTABLE_NODE_KINDS,
          autonomousCoDesign: true,
        }
      : {
          ...program.agentScopePolicy,
          autonomousCoDesign: false,
        };
    const iterations = baseRun.iterations.slice(0, Math.max(1, maxIterations));

    setProgram({
      ...freshProgram,
      agentScopePolicy: policy,
      coDesignRuns: freshProgram.coDesignRuns.map((run) =>
        run.id === baseRun.id
          ? {
              ...run,
              actorMode: autonomousMode ? "autonomous_ai" : "human_gated",
              status: "running",
              startedAt: new Date().toISOString(),
              completedAt: undefined,
              latestSummary: autonomousMode
                ? "Autonomous replay active — review queue bypassed for this run."
                : "Human-gated replay active — derived artifacts still require review.",
              goal: {
                ...run.goal,
                objective: goal,
                maxIterations: Math.max(1, maxIterations),
              },
              iterations,
            }
          : run,
      ),
    });
    setSelectedIterationId(null);
    setView("coDesign");

    let index = 0;
    runTimerRef.current = window.setInterval(() => {
      const nextIteration = iterations[index];
      if (!nextIteration) {
        if (runTimerRef.current != null) window.clearInterval(runTimerRef.current);
        runTimerRef.current = null;
        return;
      }

      setProgram((current) =>
        applyIterationToProgram(
          current,
          baseRun.id,
          nextIteration,
          autonomousMode,
          index === iterations.length - 1,
          maxIterations,
          baseRun.iterations.length,
        ),
      );
      setSelectedIterationId(nextIteration.id);

      const firstMutation = nextIteration.mutations[0];
      if (firstMutation) {
        setSelection({
          kind: toUiNodeKind(firstMutation.nodeKind),
          id: firstMutation.nodeId,
        });
      }

      index += 1;
      if (index >= iterations.length && runTimerRef.current != null) {
        window.clearInterval(runTimerRef.current);
        runTimerRef.current = null;
      }
    }, 1200);
  }

  return (
    <AppShell
      programName={program.name}
      configurations={program.configurations}
      activeConfigurationId={program.activeConfigurationId}
      activeConfigurationLabel={activeConfig?.name ?? "—"}
      view={view}
      reviewCount={reviewCount}
      aiWarningCount={aiWarningCount}
      onViewChange={setView}
      onConfigurationChange={setActiveConfiguration}
    >
      {view === "graph" && (
        <SsotGraphView
          model={model}
          selectedId={selectedId}
          onSelect={navigate}
        />
      )}

      {view === "requirements" && (
        <div className="split-view">
          <aside className="panel panel-list">
            <header className="panel-header">
              <h2>Requirements</h2>
              <div className="level-tabs" role="tablist">
                <button
                  type="button"
                  className={levelFilter === "all" ? "active" : ""}
                  onClick={() => setLevelFilter("all")}
                >
                  All
                </button>
                {LEVEL_ORDER.map((level) => (
                  <button
                    key={level}
                    type="button"
                    className={levelFilter === level ? "active" : ""}
                    onClick={() => setLevelFilter(level)}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </header>
            <RequirementsTree
              requirements={requirements}
              elements={model.elements}
              selectedId={
                selection.kind === "requirement" ? selectedId : null
              }
              onSelect={(id) => navigate("requirement", id)}
            />
          </aside>
          <div className="panel panel-detail">
            {selectedRequirement ? (
              <>
                <RequirementDetail
                  requirement={selectedRequirement}
                  element={model.elements.find(
                    (e) => e.id === selectedRequirement.assignedElementId,
                  )}
                  onAdvanceLifecycle={advanceRequirementLifecycle}
                />
                <ProvenancePanel
                  records={program.provenanceRecords}
                  nodeId={selectedRequirement.id}
                />
                {linkedConstraints.length > 0 && (
                  <div className="detail-block">
                    <h3>Design constraints</h3>
                    <ul>
                      {linkedConstraints.map((c) => (
                        <li key={c.id}>
                          <button
                            type="button"
                            className="link-button"
                            onClick={() => navigate("constraint", c.id)}
                          >
                            <span className="req-key">{c.key}</span> {c.title}
                            {c.actsAsFunctionalRequirement && (
                              <span className="tag tag-functional"> V&amp;V</span>
                            )}
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <GraphLinksPanel
                  model={model}
                  nodeId={selectedRequirement.id}
                  nodeKind="requirement"
                  onNavigate={navigate}
                />
              </>
            ) : (
              <p className="empty-state">Select a requirement.</p>
            )}
          </div>
        </div>
      )}

      {view === "interfaces" && (
        <InterfaceView
          model={model}
          selectedId={selection.kind === "icd" ? selectedId : null}
          onSelect={(id) => setSelection({ kind: "icd", id })}
          onNavigate={navigate}
        />
      )}

      {view === "design" && (
        <DesignView
          model={model}
          provenanceRecords={program.provenanceRecords}
          tab={designTab}
          onTabChange={setDesignTab}
          selectedId={
            selection.kind === "parameter" || selection.kind === "constraint"
              ? selectedId
              : null
          }
          onSelect={(id) =>
            setSelection({
              kind: designTab === "parameters" ? "parameter" : "constraint",
              id,
            })
          }
          onNavigate={navigate}
        />
      )}

      {view === "cad" && (
        <CadView
          model={model}
          selectedId={selection.kind === "cad" ? selectedId : null}
          onSelect={(id) => setSelection({ kind: "cad", id })}
          onNavigate={navigate}
        />
      )}

      {view === "integration" && (
        <DesignIntegrationView
          model={model}
          integrationRuns={program.integrationRuns}
          selectedBindingId={selectedBindingId}
          onSelectBinding={setSelectedBindingId}
        />
      )}

      {view === "coDesign" && (
        <CoDesignView
          run={activeCoDesignRun}
          model={model}
          provenanceRecords={program.provenanceRecords}
          selectedGraphNodeId={selectedId}
          selectedIterationId={selectedIterationId}
          autonomousMode={isAutonomousCoDesign(program.agentScopePolicy)}
          reviewBypassed={reviewBypassed}
          onSelectGraphNode={navigate}
          onSelectIteration={setSelectedIterationId}
          onStartRun={startCoDesignRun}
          onStopRun={stopCoDesignRun}
        />
      )}

      {view === "policy" && (
        <AgentPolicyView
          policy={program.agentScopePolicy}
          provenanceRecords={program.provenanceRecords}
          onPolicyChange={setAgentScopePolicy}
        />
      )}

      {view === "matrix" && (
        <ComplianceMatrix
          subjects={matrixSubjects}
          activities={program.verificationActivities}
          cells={program.matrixCells}
          selectedSubjectId={selectedId}
          onSelectSubject={(id) => {
            const sub = matrixSubjects.find((s) => s.id === id);
            if (sub?.source === "constraint") navigate("constraint", id);
            else navigate("requirement", id);
          }}
        />
      )}

      {view === "review" && (
        <ReviewQueue
          requirements={model.requirements}
          constraints={model.designConstraints}
          bypassed={reviewBypassed}
          selectedId={selectedId}
          onSelect={(id, kind) => setSelection({ kind, id })}
          onAdvanceRequirement={advanceRequirementLifecycle}
          onAdvanceConstraint={advanceConstraintLifecycle}
        />
      )}
    </AppShell>
  );
}

function applyIterationToProgram(
  program: Program,
  runId: EntityId,
  iteration: CoDesignIteration,
  autonomousMode: boolean,
  isFinalIteration: boolean,
  maxIterations: number,
  templateLength: number,
): Program {
  let nextProgram: Program = {
    ...program,
    model: {
      ...program.model,
      requirements: [...program.model.requirements],
      interfaceControlDocuments: [...program.model.interfaceControlDocuments],
      interfaceParameters: [...program.model.interfaceParameters],
      designParameters: [...program.model.designParameters],
      designConstraints: [...program.model.designConstraints],
    },
    provenanceRecords: [...program.provenanceRecords],
    integrationRuns: [...program.integrationRuns],
    matrixCells: [...program.matrixCells],
    coDesignRuns: program.coDesignRuns.map((run) =>
      run.id === runId
        ? {
            ...run,
            selectedIterationId: iteration.id,
            latestSummary: iteration.summary,
          }
        : run,
    ),
  };

  for (const mutation of iteration.mutations) {
    nextProgram = applyMutation(nextProgram, mutation, autonomousMode);
  }

  for (const generated of iteration.generatedIntegrationRuns ?? []) {
    if (!nextProgram.integrationRuns.some((run) => run.id === generated.id)) {
      nextProgram.integrationRuns.push(generated);
    }
  }

  for (const record of iteration.generatedProvenanceRecords ?? []) {
    if (!nextProgram.provenanceRecords.some((existing) => existing.id === record.id)) {
      nextProgram.provenanceRecords.push(record);
    }
  }

  const latestEvidence =
    iteration.generatedIntegrationRuns?.at(-1)?.evidenceRef ??
    findIntegrationRun(nextProgram.integrationRuns, iteration.integrationRunIds.at(-1))
      ?.evidenceRef;
  for (const check of iteration.requirementChecks) {
    nextProgram.matrixCells = nextProgram.matrixCells.map((cell) =>
      cell.requirementId === check.requirementId && cell.activityId === "va-6"
        ? {
            ...cell,
            status: mapCheckToMatrixStatus(check.status),
            note: check.note,
            evidenceRef: latestEvidence ?? cell.evidenceRef,
          }
        : cell,
    );
  }

  nextProgram.coDesignRuns = nextProgram.coDesignRuns.map((run) =>
    run.id === runId
      ? {
          ...run,
          status: isFinalIteration
            ? maxIterations < templateLength
              ? "max_iterations"
              : "converged"
            : "running",
          completedAt: isFinalIteration ? new Date().toISOString() : run.completedAt,
          latestSummary: isFinalIteration
            ? autonomousMode
              ? "Run converged in autonomous mode."
              : "Run replay complete — derived outputs remain queued for human review."
            : iteration.summary,
        }
      : run,
  );

  return nextProgram;
}

function applyMutation(
  program: Program,
  mutation: CoDesignIteration["mutations"][number],
  autonomousMode: boolean,
): Program {
  switch (mutation.nodeKind) {
    case "design_parameter":
      return {
        ...program,
        model: {
          ...program.model,
          designParameters: program.model.designParameters.map((parameter) =>
            parameter.id === mutation.nodeId
              ? {
                  ...parameter,
                  value: castFieldValue(parameter.value, mutation.newValue),
                }
              : parameter,
          ),
        },
      };
    case "design_constraint":
      return {
        ...program,
        model: {
          ...program.model,
          designConstraints: program.model.designConstraints.map((constraint) =>
            constraint.id === mutation.nodeId
              ? {
                  ...constraint,
                  state:
                    mutation.fieldPath === "state"
                      ? castLifecycleState(
                          mutation.newValue,
                          autonomousMode ? "baseline" : "under_review",
                        )
                      : constraint.state,
                  statement:
                    mutation.fieldPath === "statement"
                      ? mutation.newValue
                      : constraint.statement,
                }
              : constraint,
          ),
        },
      };
    case "requirement":
      return {
        ...program,
        model: {
          ...program.model,
          requirements: program.model.requirements.map((requirement) =>
            requirement.id === mutation.nodeId
              ? {
                  ...requirement,
                  state:
                    mutation.fieldPath === "state"
                      ? castLifecycleState(
                          mutation.newValue,
                          autonomousMode ? "baseline" : "under_review",
                        )
                      : requirement.state,
                  statement:
                    mutation.fieldPath === "statement"
                      ? mutation.newValue
                      : requirement.statement,
                }
              : requirement,
          ),
        },
      };
    case "icd":
      return {
        ...program,
        model: {
          ...program.model,
          interfaceControlDocuments: program.model.interfaceControlDocuments.map((icd) =>
            icd.id === mutation.nodeId
              ? {
                  ...icd,
                  scope: mutation.fieldPath === "scope" ? mutation.newValue : icd.scope,
                }
              : icd,
          ),
        },
      };
    case "interface_parameter":
      return {
        ...program,
        model: {
          ...program.model,
          interfaceParameters: program.model.interfaceParameters.map((parameter) =>
            parameter.id === mutation.nodeId
              ? {
                  ...parameter,
                  nominal:
                    mutation.fieldPath === "nominal"
                      ? Number(mutation.newValue)
                      : parameter.nominal,
                }
              : parameter,
          ),
        },
      };
    default:
      return program;
  }
}

function castFieldValue(
  current: string | number | boolean,
  nextValue: string,
): string | number | boolean {
  if (typeof current === "number") return Number(nextValue);
  if (typeof current === "boolean") return nextValue === "true";
  return nextValue;
}

function castLifecycleState(
  value: string,
  fallback: LifecycleState,
): LifecycleState {
  if (
    value === "draft" ||
    value === "under_review" ||
    value === "baseline" ||
    value === "obsolete"
  ) {
    return value;
  }
  return fallback;
}

function mapCheckToMatrixStatus(
  status: CoDesignIteration["requirementChecks"][number]["status"],
): "planned" | "pass" | "fail" | "gap" {
  switch (status) {
    case "pass":
      return "pass";
    case "fail":
      return "fail";
    case "blocked":
      return "gap";
    case "improving":
    default:
      return "planned";
  }
}

function findIntegrationRun(
  runs: IntegrationRun[],
  id: EntityId | undefined,
): IntegrationRun | undefined {
  if (!id) return undefined;
  return runs.find((run) => run.id === id);
}

function toUiNodeKind(
  kind: CoDesignIteration["mutations"][number]["nodeKind"],
): SsotNodeKind {
  switch (kind) {
    case "design_parameter":
      return "parameter";
    case "design_constraint":
      return "constraint";
    case "icd":
      return "icd";
    case "requirement":
      return "requirement";
    default:
      return "element";
  }
}
