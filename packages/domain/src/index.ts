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
}

/** Requirements that participate in V&V closure (functional + acting constraints) */
export function isVerificationSubject(req: Requirement): boolean {
  return req.kind === "functional" || req.kind === "stakeholder";
}

export function isVerificationSubjectConstraint(c: DesignConstraint): boolean {
  return c.actsAsFunctionalRequirement;
}
