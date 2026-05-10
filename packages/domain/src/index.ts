/** Unique identifier for persisted entities */
export type EntityId = string;

/** Lifecycle of a requirement or spec artifact */
export type LifecycleState = "draft" | "under_review" | "baseline" | "obsolete";

export interface Requirement {
  id: EntityId;
  key: string;
  title: string;
  statement: string;
  rationale?: string;
  state: LifecycleState;
  parentId?: EntityId;
}

/** Abstract system element (subsystem, assembly, component, interface) */
export interface SystemElement {
  id: EntityId;
  name: string;
  kind: "system" | "subsystem" | "assembly" | "component" | "interface";
  parentId?: EntityId;
}

/** Directed trace link (e.g. satisfies, verifies, implements) */
export interface TraceLink {
  id: EntityId;
  relation: "satisfies" | "verifies" | "implements" | "derives_from";
  sourceId: EntityId;
  targetId: EntityId;
}

export interface SystemsModel {
  requirements: Requirement[];
  elements: SystemElement[];
  traces: TraceLink[];
}
