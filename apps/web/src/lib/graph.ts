import type {
  CadModel,
  DesignConstraint,
  DesignParameter,
  EngineeringGraph,
  EntityId,
  InterfaceControlDocument,
  Requirement,
  TraceLink,
} from "@one-piece/domain";
import { isVerificationSubjectConstraint } from "@one-piece/domain";

export type SsotNodeKind =
  | "requirement"
  | "icd"
  | "parameter"
  | "constraint"
  | "cad"
  | "element";

export interface SsotNodeRef {
  kind: SsotNodeKind;
  id: EntityId;
}

export interface VerificationSubject {
  id: EntityId;
  key: string;
  title: string;
  source: "requirement" | "constraint";
}

export function getVerificationSubjects(
  model: EngineeringGraph,
): VerificationSubject[] {
  const fromReqs = model.requirements
    .filter((r) => r.kind === "functional" || r.kind === "stakeholder")
    .map((r) => ({
      id: r.id,
      key: r.key,
      title: r.title,
      source: "requirement" as const,
    }));

  const fromConstraints = model.designConstraints
    .filter(isVerificationSubjectConstraint)
    .map((c) => ({
      id: c.id,
      key: c.key,
      title: c.title,
      source: "constraint" as const,
    }));

  return [...fromReqs, ...fromConstraints];
}

export function tracesForNode(
  traces: TraceLink[],
  nodeId: EntityId,
): { outgoing: TraceLink[]; incoming: TraceLink[] } {
  return {
    outgoing: traces.filter((t) => t.sourceId === nodeId),
    incoming: traces.filter((t) => t.targetId === nodeId),
  };
}

export interface ResolvedTraceEnd {
  kind: SsotNodeKind;
  id: EntityId;
  key: string;
  label: string;
}

export function resolveNode(
  model: EngineeringGraph,
  id: EntityId,
): ResolvedTraceEnd | undefined {
  const r = model.requirements.find((x) => x.id === id);
  if (r) return { kind: "requirement", id, key: r.key, label: r.title };

  const icd = model.interfaceControlDocuments.find((x) => x.id === id);
  if (icd) return { kind: "icd", id, key: icd.key, label: icd.title };

  const p = model.designParameters.find((x) => x.id === id);
  if (p) return { kind: "parameter", id, key: p.key, label: p.name };

  const c = model.designConstraints.find((x) => x.id === id);
  if (c) return { kind: "constraint", id, key: c.key, label: c.title };

  const cad = model.cadModels.find((x) => x.id === id);
  if (cad) return { kind: "cad", id, key: cad.key, label: cad.name };

  const el = model.elements.find((x) => x.id === id);
  if (el) return { kind: "element", id, key: el.kind, label: el.name };

  return undefined;
}

export function linkedParametersForIcd(
  model: EngineeringGraph,
  icdId: EntityId,
): DesignParameter[] {
  const paramIds = model.interfaceParameters
    .filter((p) => p.icdId === icdId && p.designParameterId)
    .map((p) => p.designParameterId as EntityId);
  return model.designParameters.filter((p) => paramIds.includes(p.id));
}

export function linkedConstraintsForRequirement(
  model: EngineeringGraph,
  reqId: EntityId,
): DesignConstraint[] {
  const ids = model.traces
    .filter((t) => t.relation === "constrains" && t.targetId === reqId)
    .map((t) => t.sourceId);
  return model.designConstraints.filter((c) => ids.includes(c.id));
}

export function cadForElement(
  model: EngineeringGraph,
  elementId: EntityId,
): CadModel[] {
  return model.cadModels.filter((c) => c.elementId === elementId);
}

export function icdsForElement(
  model: EngineeringGraph,
  elementId: EntityId,
): InterfaceControlDocument[] {
  return model.interfaceControlDocuments.filter(
    (i) =>
      i.providerElementId === elementId || i.consumerElementId === elementId,
  );
}

export function requirementById(
  model: EngineeringGraph,
  id: EntityId,
): Requirement | undefined {
  return model.requirements.find((r) => r.id === id);
}
