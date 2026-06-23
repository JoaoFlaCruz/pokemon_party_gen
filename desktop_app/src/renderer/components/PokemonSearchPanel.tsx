import type { PokemonFilters, PokemonSummary } from "../types/domain";
import { EmptyState } from "./AppShell";

type Props = {
  filters: PokemonFilters;
  results: PokemonSummary[];
  types: string[];
  onFiltersChange(filters: PokemonFilters): void;
  onSelectPokemon(pokemonId: number): void;
};

export function PokemonSearchPanel({ filters, results, types, onFiltersChange, onSelectPokemon }: Props) {
  return (
    <section className="panel search-panel">
      <h2>Pokemon</h2>
      <div className="filters">
        <input aria-label="Nome" placeholder="Nome" value={filters.name ?? ""} onChange={(event) => onFiltersChange({ ...filters, name: event.target.value })} />
        <input
          aria-label="Numero Pokedex"
          placeholder="Numero"
          type="number"
          value={filters.pokedexNumber ?? ""}
          onChange={(event) => onFiltersChange({ ...filters, pokedexNumber: event.target.value ? Number(event.target.value) : undefined })}
        />
        <select aria-label="Tipo A" value={filters.typeA ?? ""} onChange={(event) => onFiltersChange({ ...filters, typeA: event.target.value || undefined })}>
          <option value="">Tipo A</option>
          {types.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
        <select aria-label="Tipo B" value={filters.typeB ?? ""} onChange={(event) => onFiltersChange({ ...filters, typeB: event.target.value || undefined })}>
          <option value="">Tipo B</option>
          {types.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>
      {results.length === 0 ? (
        <EmptyState title="Nenhum Pokemon encontrado." />
      ) : (
        <div className="pokemon-results">
          {results.map((pokemon) => (
            <button key={pokemon.id} onClick={() => onSelectPokemon(pokemon.id)}>
              <img src={pokemon.spriteUrl} alt="" />
              <span>#{pokemon.pokedexNumber} {pokemon.name}</span>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
