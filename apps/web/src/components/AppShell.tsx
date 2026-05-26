import type { EntityId, ProgramConfiguration } from "@one-piece/domain";
import type { ReactNode } from "react";

export type AppView =
  | "graph"
  | "requirements"
  | "interfaces"
  | "design"
  | "cad"
  | "integration"
  | "policy"
  | "matrix"
  | "review";

interface AppShellProps {
  programName: string;
  configurations: ProgramConfiguration[];
  activeConfigurationId: EntityId;
  activeConfigurationLabel: string;
  view: AppView;
  reviewCount: number;
  aiWarningCount?: number;
  onViewChange: (view: AppView) => void;
  onConfigurationChange: (id: EntityId) => void;
  children: ReactNode;
}

const NAV: { id: AppView; label: string }[] = [
  { id: "graph", label: "SSOT graph" },
  { id: "requirements", label: "Requirements" },
  { id: "interfaces", label: "Interfaces (ICD)" },
  { id: "design", label: "Design" },
  { id: "cad", label: "CAD" },
  { id: "integration", label: "Design integration" },
  { id: "policy", label: "Actor boundaries" },
  { id: "matrix", label: "Compliance matrix" },
  { id: "review", label: "Review queue" },
];

export function AppShell({
  programName,
  configurations,
  activeConfigurationId,
  activeConfigurationLabel,
  view,
  reviewCount,
  aiWarningCount = 0,
  onViewChange,
  onConfigurationChange,
  children,
}: AppShellProps) {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">1P</span>
          <span className="brand-name">one-piece</span>
        </div>
        <p className="program-label">Program</p>
        <p className="program-name">{programName}</p>

        <label className="field-label" htmlFor="config-select">
          Configuration
        </label>
        <select
          id="config-select"
          className="config-select"
          value={activeConfigurationId}
          onChange={(e) => onConfigurationChange(e.target.value)}
        >
          {configurations.map((c) => (
            <option key={c.id} value={c.id}>
              {c.key} — {c.name}
            </option>
          ))}
        </select>
        <p className="config-hint">{activeConfigurationLabel}</p>

        <nav className="sidebar-nav" aria-label="Main">
          {NAV.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`nav-item ${view === item.id ? "active" : ""}`}
              onClick={() => onViewChange(item.id)}
            >
              {item.label}
              {item.id === "review" && reviewCount > 0 && (
                <span className="badge">{reviewCount}</span>
              )}
              {item.id === "policy" && aiWarningCount > 0 && (
                <span className="badge badge-warn">{aiWarningCount}</span>
              )}
            </button>
          ))}
        </nav>

        <p className="sidebar-foot">
          SSOT graph — requirements, ICD, parameters, constraints, CAD, V&amp;V.
        </p>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
