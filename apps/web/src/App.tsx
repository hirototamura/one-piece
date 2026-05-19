import { useMemo, useState } from "react";
import type {
  EntityId,
  LifecycleState,
  Program,
  Requirement,
  RequirementLevel,
} from "@one-piece/domain";
import "./App.css";
import { demoProgram } from "./data/demoProgram";
import { AppShell, type AppView } from "./components/AppShell";
import { CadView } from "./components/CadView";
import { ComplianceMatrix } from "./components/ComplianceMatrix";
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

export function App() {
  const [program, setProgram] = useState<Program>(demoProgram);
  const [view, setView] = useState<AppView>("graph");
  const [selection, setSelection] = useState<{
    kind: SsotNodeKind;
    id: EntityId;
  }>({ kind: "requirement", id: "req-s1" });
  const [designTab, setDesignTab] = useState<"parameters" | "constraints">(
    "parameters",
  );
  const [levelFilter, setLevelFilter] = useState<RequirementLevel | "all">(
    "all",
  );

  const { model } = program;
  const selectedId = selection.id;

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

  return (
    <AppShell
      programName={program.name}
      configurations={program.configurations}
      activeConfigurationId={program.activeConfigurationId}
      activeConfigurationLabel={activeConfig?.name ?? "—"}
      view={view}
      reviewCount={reviewItems.length}
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
          selectedId={selectedId}
          onSelect={(id, kind) => setSelection({ kind, id })}
          onAdvanceRequirement={advanceRequirementLifecycle}
          onAdvanceConstraint={advanceConstraintLifecycle}
        />
      )}
    </AppShell>
  );
}
