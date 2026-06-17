import type { PokemonSummary } from "../types/domain";
import type { SavedTeam } from "../types/app-state";

export function SavedTeamCard({ team, pokemonById }: { team: SavedTeam; pokemonById: Map<number, PokemonSummary> }) {
  const versionWarning = team.contractVersion !== "fixture-1";
  return (
    <article className="saved-team-card">
      <header>
        <h3>{team.name}</h3>
        {versionWarning ? <span className="warning">Versao de contrato diferente</span> : null}
      </header>
      <div className="saved-slots">
        {team.slots.map((slot) => {
          const pokemon = slot.pokemonId ? pokemonById.get(slot.pokemonId) : null;
          return (
            <div key={slot.position} className="saved-slot">
              <span>#{slot.position}</span>
              {pokemon ? <img src={pokemon.spriteUrl} alt={pokemon.name} /> : <span>Vazio</span>}
              <strong>{pokemon?.name ?? "Vazio"}</strong>
            </div>
          );
        })}
      </div>
    </article>
  );
}
