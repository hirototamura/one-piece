import type { EntityId, Requirement, SystemElement } from "@one-piece/domain";
import { StateBadge } from "./StateBadge";

interface RequirementsTreeProps {
  requirements: Requirement[];
  elements: SystemElement[];
  selectedId: EntityId | null;
  onSelect: (id: EntityId) => void;
}

export function RequirementsTree({
  requirements,
  elements,
  selectedId,
  onSelect,
}: RequirementsTreeProps) {
  const byParent = new Map<string | undefined, Requirement[]>();
  for (const r of requirements) {
    const key = r.parentId;
    const list = byParent.get(key) ?? [];
    list.push(r);
    byParent.set(key, list);
  }

  function renderLevel(parentId: string | undefined, depth: number) {
    const nodes = byParent.get(parentId) ?? [];
    return nodes.map((req) => {
      const element = elements.find((e) => e.id === req.assignedElementId);
      return (
        <li key={req.id} className="tree-node">
          <button
            type="button"
            className={`tree-row ${selectedId === req.id ? "selected" : ""}`}
            style={{ paddingLeft: `${12 + depth * 16}px` }}
            onClick={() => onSelect(req.id)}
          >
            <span className="req-key">{req.key}</span>
            <span className="req-title">{req.title}</span>
            <StateBadge state={req.state} />
          </button>
          {element && (
            <span className="tree-meta" style={{ paddingLeft: `${28 + depth * 16}px` }}>
              {element.name}
            </span>
          )}
          <ul className="tree-children">
            {renderLevel(req.id, depth + 1)}
          </ul>
        </li>
      );
    });
  }

  const roots = byParent.get(undefined) ?? [];

  if (roots.length === 0) {
    return <p className="empty-state">No requirements at this level.</p>;
  }

  return <ul className="req-tree">{renderLevel(undefined, 0)}</ul>;
}
