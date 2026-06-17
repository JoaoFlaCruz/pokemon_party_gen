import type { ReactNode } from "react";
import type { Diagnostic } from "../types/domain";
import type { AppView } from "../types/app-state";

type Props = {
  currentView: AppView;
  diagnostics: Diagnostic[];
  onNavigate(view: AppView): void;
  children: ReactNode;
};

export function AppShell({ currentView, diagnostics, onNavigate, children }: Props) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>Pokemon Party Generator</h1>
        <nav aria-label="Primary navigation">
          <button className={currentView === "team-builder" ? "active" : ""} onClick={() => onNavigate("team-builder")}>
            Montagem
          </button>
          <button className={currentView === "saved-teams" ? "active" : ""} onClick={() => onNavigate("saved-teams")}>
            Times Salvos
          </button>
        </nav>
      </header>
      <DiagnosticBanner diagnostics={diagnostics} />
      {children}
    </div>
  );
}

export function DiagnosticBanner({ diagnostics }: { diagnostics: Diagnostic[] }) {
  if (!diagnostics.length) return null;
  return (
    <section className="diagnostics" aria-label="Diagnostics">
      {diagnostics.map((diagnostic, index) => (
        <p key={`${diagnostic.code}-${index}`} className={`diagnostic ${diagnostic.severity}`}>
          {diagnostic.message}
        </p>
      ))}
    </section>
  );
}

export function EmptyState({ title, action }: { title: string; action?: React.ReactNode }) {
  return (
    <div className="empty-state">
      <p>{title}</p>
      {action}
    </div>
  );
}
