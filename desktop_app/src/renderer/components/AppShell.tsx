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
      <header className="retro-topbar" aria-label="Barra Superior">
        <div className="topbar-left">
          <span className="topbar-tag-data">DADOS</span>
        </div>

        <nav className="topbar-center" aria-label="Navegação Principal">
          <button
            type="button"
            className={`topbar-btn btn-team ${currentView === "team-builder" ? "active" : ""}`}
            onClick={() => onNavigate("team-builder")}
            title="Montagem de Time"
          >
            EQUIPE POKEMON
            <span className="sr-only">Montagem</span>
          </button>

          <button
            type="button"
            className={`topbar-btn btn-close-box ${currentView === "saved-teams" ? "active" : ""}`}
            onClick={() => onNavigate("saved-teams")}
            title="Fechar Caixa e Ver Times Salvos"
          >
            FECHAR CAIXA
            <span className="sr-only">Times Salvos</span>
          </button>
        </nav>

        <div className="topbar-right">
          <button
            type="button"
            className="topbar-btn btn-manager"
            onClick={() => {
              if (currentView !== "team-builder") {
                onNavigate("team-builder");
              }
            }}
          >
            GERENCIADOR
          </button>
        </div>
      </header>

      <DiagnosticBanner diagnostics={diagnostics} />
      <div className="app-main-content">{children}</div>
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
