import type { EngineeringGraph, EntityId, TraceLink } from "@one-piece/domain";
import { resolveNode, tracesForNode, type SsotNodeKind } from "../lib/graph";

interface GraphLinksPanelProps {
  model: EngineeringGraph;
  nodeId: EntityId;
  nodeKind: SsotNodeKind;
  onNavigate: (kind: SsotNodeKind, id: EntityId) => void;
}

function LinkSection({
  title,
  links,
  model,
  direction,
  onNavigate,
}: {
  title: string;
  links: TraceLink[];
  model: EngineeringGraph;
  direction: "out" | "in";
  onNavigate: (kind: SsotNodeKind, id: EntityId) => void;
}) {
  if (links.length === 0) return null;

  return (
    <div className="trace-block">
      <h3>{title}</h3>
      <ul>
        {links.map((link) => {
          const otherId = direction === "out" ? link.targetId : link.sourceId;
          const node = resolveNode(model, otherId);
          if (!node) return null;
          return (
            <li key={link.id}>
              <span className="trace-relation">{link.relation}</span>
              <button
                type="button"
                className="link-button"
                onClick={() => onNavigate(node.kind, node.id)}
              >
                <span className="node-kind">{node.kind}</span>
                <span className="req-key">{node.key}</span> {node.label}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export function GraphLinksPanel({
  model,
  nodeId,
  onNavigate,
}: GraphLinksPanelProps) {
  const { outgoing, incoming } = tracesForNode(model.traces, nodeId);
  const self = resolveNode(model, nodeId);

  return (
    <section className="trace-panel">
      <h2>Graph links</h2>
      {self && (
        <p className="muted">
          <span className="node-kind">{self.kind}</span>{" "}
          <span className="req-key">{self.key}</span>
        </p>
      )}
      <LinkSection
        title="Outgoing"
        links={outgoing}
        model={model}
        direction="out"
        onNavigate={onNavigate}
      />
      <LinkSection
        title="Incoming"
        links={incoming}
        model={model}
        direction="in"
        onNavigate={onNavigate}
      />
      {!outgoing.length && !incoming.length && (
        <p className="muted">No trace links for this node.</p>
      )}
    </section>
  );
}
