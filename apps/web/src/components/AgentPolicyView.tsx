import type {
  AgentScopePolicy,
  EntityId,
  SsotMutableNodeKind,
  SsotProvenanceRecord,
} from "@one-piece/domain";
import { aiTouchesInHumanDomain } from "@one-piece/domain";
import { ActorBadge } from "./ActorBadge";

interface AgentPolicyViewProps {
  policy: AgentScopePolicy;
  provenanceRecords: SsotProvenanceRecord[];
  onPolicyChange: (policy: AgentScopePolicy) => void;
}

const NODE_KIND_LABELS: Record<SsotMutableNodeKind, string> = {
  requirement: "Requirements",
  design_parameter: "Design parameters",
  design_constraint: "Design constraints",
  interface_parameter: "Interface parameters",
  icd: "ICDs",
};

const ALL_NODE_KINDS: SsotMutableNodeKind[] = [
  "requirement",
  "design_parameter",
  "design_constraint",
  "interface_parameter",
  "icd",
];

export function AgentPolicyView({
  policy,
  provenanceRecords,
  onPolicyChange,
}: AgentPolicyViewProps) {
  const aiWarnings = aiTouchesInHumanDomain(provenanceRecords);

  function toggleNodeKind(kind: SsotMutableNodeKind) {
    const allowed = policy.allowedNodeKinds.includes(kind)
      ? policy.allowedNodeKinds.filter((k) => k !== kind)
      : [...policy.allowedNodeKinds, kind];
    onPolicyChange({ ...policy, allowedNodeKinds: allowed });
  }

  return (
    <div className="policy-view">
      <header className="panel-header">
        <div>
          <h2>Actor boundaries</h2>
          <p className="panel-subtitle">
            SSOT updates come from human engineers, logic automation, or AI agents.
            Critical items stay human-owned; AI scope is admin-configurable.
          </p>
        </div>
      </header>

      <div className="policy-grid">
        <section className="detail-block policy-card">
          <h3>AI agent scope (admin)</h3>
          <label className="field-inline" htmlFor="ai-fraction">
            Allowed fraction of non-critical mutations
          </label>
          <div className="fraction-control">
            <input
              id="ai-fraction"
              type="range"
              min={0}
              max={100}
              value={Math.round(policy.allowedFraction * 100)}
              onChange={(e) =>
                onPolicyChange({
                  ...policy,
                  allowedFraction: Number(e.target.value) / 100,
                })
              }
            />
            <span className="fraction-value">
              {Math.round(policy.allowedFraction * 100)}%
            </span>
          </div>
          <p className="hint">
            Default ~20%. AI may not mutate critical-tier artifacts or kinds outside
            this list.
          </p>

          <h4>Allowed node kinds for AI</h4>
          <ul className="checkbox-list">
            {ALL_NODE_KINDS.map((kind) => (
              <li key={kind}>
                <label>
                  <input
                    type="checkbox"
                    checked={policy.allowedNodeKinds.includes(kind)}
                    onChange={() => toggleNodeKind(kind)}
                  />
                  {NODE_KIND_LABELS[kind]}
                </label>
              </li>
            ))}
          </ul>

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={policy.requireProvenanceDisclosure}
              onChange={(e) =>
                onPolicyChange({
                  ...policy,
                  requireProvenanceDisclosure: e.target.checked,
                })
              }
            />
            Require visible AI provenance in human-dominated areas
          </label>
        </section>

        <section className="detail-block policy-card">
          <h3>Actor roles</h3>
          <dl className="actor-legend">
            <dt>
              <ActorBadge kind="human_engineer" />
            </dt>
            <dd>
              Interfaces with the real world; owns critical design rationale and
              baselines.
            </dd>
            <dt>
              <ActorBadge kind="logic_automation" />
            </dt>
            <dd>
              Deterministic connectors (Excel→Python sync, CI runners). No LLM.
            </dd>
            <dt>
              <ActorBadge kind="ai_agent" />
            </dt>
            <dd>
              Drafts within configured scope; must leave provenance where humans
              decide.
            </dd>
          </dl>
        </section>
      </div>

      {aiWarnings.length > 0 && (
        <section className="detail-block ai-alert-panel">
          <h3>
            AI touches in human domain
            <span className="badge badge-warn">{aiWarnings.length}</span>
          </h3>
          <p className="hint">
            These mutations were performed by an AI agent on artifacts where human
            judgment is primary. Verify design rationale before accepting.
          </p>
          <ul className="provenance-list">
            {aiWarnings.map((r) => (
              <ProvenanceRow key={r.id} record={r} highlight />
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

export function ProvenancePanel({
  records,
  nodeId,
  limit = 5,
}: {
  records: SsotProvenanceRecord[];
  nodeId: EntityId;
  limit?: number;
}) {
  const rows = records
    .filter((r) => r.nodeId === nodeId)
    .sort((a, b) => b.occurredAt.localeCompare(a.occurredAt))
    .slice(0, limit);

  if (rows.length === 0) return null;

  return (
    <div className="detail-block provenance-panel">
      <h3>SSOT provenance</h3>
      <ul className="provenance-list">
        {rows.map((r) => (
          <ProvenanceRow key={r.id} record={r} highlight={r.aiTouchInHumanDomain} />
        ))}
      </ul>
    </div>
  );
}

function ProvenanceRow({
  record,
  highlight,
}: {
  record: SsotProvenanceRecord;
  highlight?: boolean;
}) {
  return (
    <li className={`provenance-row${highlight ? " provenance-ai-touch" : ""}`}>
      <div className="provenance-meta">
        <ActorBadge kind={record.actorKind} aiWarning={record.aiTouchInHumanDomain} />
        <span className="provenance-time">
          {new Date(record.occurredAt).toLocaleString()}
        </span>
        <span className="provenance-actor">{record.actorLabel}</span>
      </div>
      <p className="provenance-change">
        <span className="req-key">{record.nodeKey}</span>
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
  );
}
