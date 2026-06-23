import { useEffect, useMemo, useState, type Dispatch } from "react";
import { pokemonSummaries } from "../data/demo-fixtures";
import { teamRepository } from "../services/teamRepository";
import type { AppAction } from "../state/appState";
import type { AppState, TeamListPage } from "../types/app-state";
import { EmptyState } from "../components/AppShell";
import { PaginationControls } from "../components/PaginationControls";
import { SavedTeamCard } from "../components/SavedTeamCard";

type Props = {
  state: AppState;
  dispatch: Dispatch<AppAction>;
};

export function SavedTeamsPage({ state, dispatch }: Props) {
  const [pageData, setPageData] = useState<TeamListPage | null>(null);
  const pokemonById = useMemo(() => new Map(pokemonSummaries.map((pokemon) => [pokemon.id, pokemon])), []);

  useEffect(() => {
    teamRepository.listSavedTeams(state.savedTeamsPage).then((result) => {
      setPageData(result.data);
      dispatch({ type: "setDiagnostics", diagnostics: result.diagnostics });
    });
  }, [state.savedTeams, state.savedTeamsPage, dispatch]);

  if (!pageData || pageData.results.length === 0) {
    return (
      <main className="saved-teams">
        <EmptyState title="Nenhum time salvo." action={<button onClick={() => dispatch({ type: "navigate", view: "team-builder" })}>Voltar para montagem</button>} />
      </main>
    );
  }

  return (
    <main className="saved-teams">
      <header className="page-header">
        <h2>Times Salvos</h2>
        <button onClick={() => dispatch({ type: "navigate", view: "team-builder" })}>Voltar para montagem</button>
      </header>
      <section className="saved-team-list">
        {pageData.results.map((team) => (
          <SavedTeamCard key={team.id} team={team} pokemonById={pokemonById} />
        ))}
      </section>
      <PaginationControls page={pageData.page} totalPages={pageData.totalPages} onPageChange={(page) => dispatch({ type: "setSavedTeamsPage", page })} />
    </main>
  );
}
