import type {
  EntityId,
  MatrixCell,
  MatrixCellStatus,
  VerificationActivity,
} from "@one-piece/domain";
import type { VerificationSubject } from "../lib/graph";

interface ComplianceMatrixProps {
  subjects: VerificationSubject[];
  activities: VerificationActivity[];
  cells: MatrixCell[];
  selectedSubjectId: EntityId | null;
  onSelectSubject: (id: EntityId) => void;
}

const STATUS_LABEL: Record<MatrixCellStatus, string> = {
  planned: "Planned",
  pass: "Pass",
  fail: "Fail",
  waived: "Waived",
  gap: "Gap",
};

function cellFor(
  cells: MatrixCell[],
  subjectId: EntityId,
  actId: EntityId,
): MatrixCell | undefined {
  return cells.find(
    (c) => c.requirementId === subjectId && c.activityId === actId,
  );
}

export function ComplianceMatrix({
  subjects,
  activities,
  cells,
  selectedSubjectId,
  onSelectSubject,
}: ComplianceMatrixProps) {
  return (
    <div className="panel matrix-panel">
      <header className="panel-header">
        <h2>Compliance matrix</h2>
        <p className="panel-subtitle">
          Functional requirements and design constraints (V&amp;V) × verification
          activities.
        </p>
      </header>
      <div className="matrix-scroll">
        <table className="matrix-table">
          <thead>
            <tr>
              <th className="sticky-col">Subject</th>
              {activities.map((a) => (
                <th key={a.id} title={a.title}>
                  <span className="act-key">{a.key}</span>
                  <span className="act-method">{a.method}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {subjects.map((sub) => (
              <tr
                key={sub.id}
                className={
                  selectedSubjectId === sub.id ? "selected-row" : ""
                }
                onClick={() => onSelectSubject(sub.id)}
              >
                <td className="sticky-col">
                  <span className="req-key">{sub.key}</span>
                  {sub.source === "constraint" && (
                    <span className="tag tag-functional">constraint</span>
                  )}
                  <span className="matrix-req-title">{sub.title}</span>
                </td>
                {activities.map((act) => {
                  const cell = cellFor(cells, sub.id, act.id);
                  return (
                    <td key={act.id}>
                      {cell ? (
                        <span
                          className={`matrix-cell status-${cell.status}`}
                          title={cell.note ?? cell.evidenceRef}
                        >
                          {STATUS_LABEL[cell.status]}
                        </span>
                      ) : (
                        <span className="matrix-cell matrix-empty">—</span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
