/** Unique identifier for persisted entities */
export type EntityId = string;

/** Lifecycle of a requirement or spec artifact */
export type LifecycleState = "draft" | "under_review" | "baseline" | "obsolete";

/** Engineering discipline tag for allocation and ICD ownership */
export type EngineeringDiscipline =
  | "gnc"
  | "mechanical"
  | "electrical"
  | "thermal"
  | "communications"
  | "software"
  | "systems"
  | "integration"
  | "other";

/** Requirement level in the hardware SE stack */
export type RequirementLevel =
  | "mission"
  | "system"
  | "operational"
  | "subsystem";

/**
 * Stakeholder/functional intent vs design constraint.
 * Design constraints with `actsAsFunctionalRequirement` participate in V&V closure like functional reqs.
 */
export type RequirementKind = "stakeholder" | "functional" | "design_constraint";

export interface Requirement {
  id: EntityId;
  key: string;
  title: string;
  statement: string;
  rationale?: string;
  state: LifecycleState;
  level: RequirementLevel;
  kind: RequirementKind;
  parentId?: EntityId;
  /** System element this requirement is allocated to */
  assignedElementId?: EntityId;
  owner?: string;
  discipline?: EngineeringDiscipline;
}

/** Abstract system element (subsystem, assembly, component) */
export interface SystemElement {
  id: EntityId;
  name: string;
  kind: "system" | "subsystem" | "assembly" | "component" | "interface";
  parentId?: EntityId;
  discipline?: EngineeringDiscipline;
}

/** Trace relation vocabulary for the SSOT graph */
export type TraceRelation =
  | "derives_from"
  | "satisfies"
  | "implements"
  | "verifies"
  | "constrains"
  | "documents"
  | "represents"
  | "allocated_to";

/** Directed trace link between SSOT nodes */
export interface TraceLink {
  id: EntityId;
  relation: TraceRelation;
  sourceId: EntityId;
  targetId: EntityId;
}

/**
 * Interface Control Document — authoritative agreement between two subsystems.
 * Lives in SSOT; discipline tools reference but do not replace ICD nodes.
 */
export interface InterfaceControlDocument {
  id: EntityId;
  key: string;
  title: string;
  state: LifecycleState;
  providerElementId: EntityId;
  consumerElementId: EntityId;
  scope: string;
  disciplines?: EngineeringDiscipline[];
}

/** Signal or physical quantity exchanged on an ICD */
export interface InterfaceParameter {
  id: EntityId;
  icdId: EntityId;
  name: string;
  direction: "in" | "out" | "bidirectional";
  dataType?: string;
  unit?: string;
  min?: number;
  max?: number;
  nominal?: number;
  /** Link to a shared design parameter when values are unified */
  designParameterId?: EntityId;
}

/** Named design parameter (budget, setpoint, tolerance) */
export interface DesignParameter {
  id: EntityId;
  key: string;
  name: string;
  value: number | string | boolean;
  unit?: string;
  discipline: EngineeringDiscipline;
  elementId?: EntityId;
  state: LifecycleState;
}

/**
 * Design constraint — limiting condition from detailed design.
 * When `actsAsFunctionalRequirement` is true, treated like a functional requirement
 * for allocation, trace-up, and verification closure.
 */
export interface DesignConstraint {
  id: EntityId;
  key: string;
  title: string;
  statement: string;
  state: LifecycleState;
  discipline: EngineeringDiscipline;
  elementId?: EntityId;
  actsAsFunctionalRequirement: boolean;
  parameterIds?: EntityId[];
}

export type CadSyncStatus = "synced" | "syncing" | "stale" | "error";

/**
 * CAD model registered in SSOT. Geometry files may live in PLM/object storage;
 * the SSOT node is authoritative for revision, linkage, and extracted parameters.
 * Connectors update this node on every design change (near-real-time).
 */
export interface CadModel {
  id: EntityId;
  key: string;
  name: string;
  elementId: EntityId;
  discipline: EngineeringDiscipline;
  sourceUri: string;
  revision: string;
  checksum?: string;
  syncStatus: CadSyncStatus;
  /** ISO-8601 timestamp of last successful sync into SSOT */
  lastSyncedAt: string;
  extractedParameterIds?: EntityId[];
}

/** Design iteration / configuration branch (e.g. V1, V2) */
export interface ProgramConfiguration {
  id: EntityId;
  key: string;
  name: string;
  description?: string;
}

export type VerificationMethod = "analysis" | "test" | "inspection";

export type TestPurpose = "development" | "qualification" | "acceptance";

export interface VerificationActivity {
  id: EntityId;
  key: string;
  title: string;
  method: VerificationMethod;
  purpose?: TestPurpose;
}

export type MatrixCellStatus =
  | "planned"
  | "pass"
  | "fail"
  | "waived"
  | "gap";

/** Compliance matrix cell: requirement × verification activity */
export interface MatrixCell {
  requirementId: EntityId;
  activityId: EntityId;
  status: MatrixCellStatus;
  evidenceRef?: string;
  note?: string;
}

/**
 * Who may mutate SSOT. Humans interface with the real world; logic automation is
 * deterministic; AI agents operate only within admin-configured scope.
 */
export type SsotActorKind = "human_engineer" | "logic_automation" | "ai_agent";

/** Criticality tier — critical artifacts stay human-owned by default. */
export type SsotCriticalityTier = "critical" | "standard" | "derived";

/** SSOT node kinds that can carry provenance and actor policy. */
export type SsotMutableNodeKind =
  | "requirement"
  | "design_parameter"
  | "design_constraint"
  | "interface_parameter"
  | "icd";

/** Admin-configurable scope for AI agents (default ~20% of non-critical surface). */
export interface AgentScopePolicy {
  /** Fraction of non-critical SSOT mutations AI may perform (0–1). Default 0.2. */
  allowedFraction: number;
  /** Critical tiers AI must never mutate without explicit human waiver. */
  blockedCriticalityTiers: SsotCriticalityTier[];
  /** Node kinds AI may touch when tier and quota allow. */
  allowedNodeKinds: SsotMutableNodeKind[];
  /** When true, AI touches in human-dominated areas require visible provenance. */
  requireProvenanceDisclosure: boolean;
}

/** Immutable audit record for every SSOT mutation. */
export interface SsotProvenanceRecord {
  id: EntityId;
  /** ISO-8601 */
  occurredAt: string;
  actorKind: SsotActorKind;
  actorLabel: string;
  nodeKind: SsotMutableNodeKind;
  nodeId: EntityId;
  nodeKey: string;
  fieldPath: string;
  previousValue?: string;
  newValue: string;
  criticalityTier: SsotCriticalityTier;
  /** True when AI touched a human-owned or critical artifact — surfaces warning in UI. */
  aiTouchInHumanDomain: boolean;
  rationale?: string;
}

/** Design artifact registered in SSOT (Excel workbook or Python script). */
export type DesignArtifactKind = "excel_workbook" | "python_script";

export interface DesignArtifact {
  id: EntityId;
  key: string;
  name: string;
  kind: DesignArtifactKind;
  /** Repo-relative or URI path */
  sourcePath: string;
  revision: string;
  discipline: EngineeringDiscipline;
  elementId?: EntityId;
  /** Linked SSOT parameter IDs this artifact influences or extracts from */
  linkedParameterIds?: EntityId[];
}

/**
 * Minimum integration unit: one Excel cell ↔ one Python binding marker.
 * Cell change propagates to script, then script re-runs via logic automation.
 */
export interface CellCodeBinding {
  id: EntityId;
  /** e.g. "Inputs!B4" */
  excelCellRef: string;
  excelArtifactId: EntityId;
  pythonArtifactId: EntityId;
  /** Marker in Python, e.g. "SSOT:PARAM:P-VBUS" */
  pythonMarker: string;
  /** Executable variable updated alongside the marker, e.g. "VBUS" */
  pythonAssignmentName?: string;
  /** SSOT design parameter this binding keeps in sync */
  designParameterId: EntityId;
}

export type IntegrationRunStatus = "pending" | "running" | "success" | "failed";

/** Record of Excel → Python sync → script execution (logic automation, not AI). */
export interface IntegrationRun {
  id: EntityId;
  /** ISO-8601 */
  startedAt: string;
  completedAt?: string;
  status: IntegrationRunStatus;
  triggeredBy: SsotActorKind;
  bindingIds: EntityId[];
  /** Summary output from script stdout or error message */
  outputSummary?: string;
}

/** Normalized SSOT engineering graph for one configuration */
export interface EngineeringGraph {
  requirements: Requirement[];
  elements: SystemElement[];
  traces: TraceLink[];
  interfaceControlDocuments: InterfaceControlDocument[];
  interfaceParameters: InterfaceParameter[];
  designParameters: DesignParameter[];
  designConstraints: DesignConstraint[];
  cadModels: CadModel[];
  designArtifacts: DesignArtifact[];
  cellCodeBindings: CellCodeBinding[];
}

/** @deprecated Use EngineeringGraph */
export type SystemsModel = EngineeringGraph;

/** In-memory program bundle (API persistence comes later) */
export interface Program {
  id: EntityId;
  name: string;
  configurations: ProgramConfiguration[];
  activeConfigurationId: EntityId;
  model: EngineeringGraph;
  verificationActivities: VerificationActivity[];
  matrixCells: MatrixCell[];
  agentScopePolicy: AgentScopePolicy;
  provenanceRecords: SsotProvenanceRecord[];
  integrationRuns: IntegrationRun[];
}

/** Default agent scope: ~20% of non-critical SSOT; critical stays human-only. */
export const DEFAULT_AGENT_SCOPE_POLICY: AgentScopePolicy = {
  allowedFraction: 0.2,
  blockedCriticalityTiers: ["critical"],
  allowedNodeKinds: ["design_parameter"],
  requireProvenanceDisclosure: true,
};

/** Returns whether an actor may mutate a node under current policy. */
export function canActorMutate(
  policy: AgentScopePolicy,
  actor: SsotActorKind,
  nodeKind: SsotMutableNodeKind,
  criticality: SsotCriticalityTier,
): boolean {
  if (actor === "human_engineer") return true;
  if (actor === "logic_automation") {
    return criticality !== "critical" || nodeKind === "design_parameter";
  }
  if (actor === "ai_agent") {
    if (policy.allowedFraction <= 0) return false;
    if (policy.blockedCriticalityTiers.includes(criticality)) return false;
    if (!policy.allowedNodeKinds.includes(nodeKind)) return false;
    return true;
  }
  return false;
}

/** Latest provenance for a node, if any. */
export function latestProvenanceForNode(
  records: SsotProvenanceRecord[],
  nodeId: EntityId,
): SsotProvenanceRecord | undefined {
  return records
    .filter((r) => r.nodeId === nodeId)
    .sort((a, b) => b.occurredAt.localeCompare(a.occurredAt))[0];
}

/** AI touches that occurred in human-dominated areas — must be visible to engineers. */
export function aiTouchesInHumanDomain(
  records: SsotProvenanceRecord[],
): SsotProvenanceRecord[] {
  return records.filter((r) => r.aiTouchInHumanDomain);
}

/** Requirements that participate in V&V closure (functional + acting constraints) */
export function isVerificationSubject(req: Requirement): boolean {
  return req.kind === "functional" || req.kind === "stakeholder";
}

export function isVerificationSubjectConstraint(c: DesignConstraint): boolean {
  return c.actsAsFunctionalRequirement;
}
