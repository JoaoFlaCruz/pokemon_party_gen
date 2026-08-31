import { useState } from "react";
import type { PokemonDetails, PokemonFilters, PokemonSummary } from "../types/domain";
import { formatTypeName, getTypeStyle } from "../utils/pokemonFormatters";
import { EmptyState } from "./AppShell";
import { SynergySuggestions } from "./SynergySuggestions";

type Props = {
  filters: PokemonFilters;
  results: PokemonSummary[];
  types: string[];
  activeDetails: PokemonDetails | null;
  onFiltersChange(filters: PokemonFilters): void;
  onSelectPokemon(pokemonId: number): void;
};

export function PokemonSearchPanel({
  filters,
  results,
  types,
  activeDetails,
  onFiltersChange,
  onSelectPokemon
}: Props) {
  const [hoveredPokemon, setHoveredPokemon] = useState<PokemonSummary | null>(null);
  const [activeTab, setActiveTab] = useState<"catalog" | "suggestions">("catalog");

  return (
    <aside className="panel manager-panel" aria-label="Painel de Gerenciamento">
      <header className="manager-header-bar">
        <h2 className="manager-title">GERENCIADOR</h2>
      </header>

      {/* Seletor de abas do Gerenciador */}
      <div className="manager-tabs">
        <button
          type="button"
          className={`manager-tab-btn ${activeTab === "catalog" ? "active" : ""}`}
          onClick={() => setActiveTab("catalog")}
        >
          Pokémons
        </button>
        <button
          type="button"
          className={`manager-tab-btn ${activeTab === "suggestions" ? "active" : ""}`}
          onClick={() => setActiveTab("suggestions")}
        >
          Sugestões
        </button>
      </div>

      {activeTab === "catalog" ? (
        <div className="manager-catalog-view">
          <div className="filters">
            <input
              aria-label="Nome"
              placeholder="Nome"
              value={filters.name ?? ""}
              onChange={(event) => onFiltersChange({ ...filters, name: event.target.value })}
            />
            <input
              aria-label="Numero Pokedex"
              placeholder="Número"
              type="number"
              value={filters.pokedexNumber ?? ""}
              onChange={(event) =>
                onFiltersChange({
                  ...filters,
                  pokedexNumber: event.target.value ? Number(event.target.value) : undefined
                })
              }
            />
            <select
              aria-label="Tipo A"
              value={filters.typeA ?? ""}
              onChange={(event) => onFiltersChange({ ...filters, typeA: event.target.value || undefined })}
            >
              <option value="">Tipo A</option>
              {types.map((type) => (
                <option key={type} value={type}>
                  {formatTypeName(type)}
                </option>
              ))}
            </select>
            <select
              aria-label="Tipo B"
              value={filters.typeB ?? ""}
              onChange={(event) => onFiltersChange({ ...filters, typeB: event.target.value || undefined })}
            >
              <option value="">Tipo B</option>
              {types.map((type) => (
                <option key={type} value={type}>
                  {formatTypeName(type)}
                </option>
              ))}
            </select>
          </div>

          {results.length === 0 ? (
            <EmptyState title="Nenhum Pokemon encontrado." />
          ) : (
            <div className="pokemon-results">
              {results.map((pokemon) => (
                <button
                  key={pokemon.id}
                  type="button"
                  className="pokemon-result-card"
                  onClick={() => onSelectPokemon(pokemon.id)}
                  onMouseEnter={() => setHoveredPokemon(pokemon)}
                  onMouseLeave={() => setHoveredPokemon(null)}
                  title={`Clique para inserir #${pokemon.pokedexNumber} ${pokemon.name} no time`}
                  aria-label={`Selecionar ${pokemon.name}`}
                >
                  <img className="catalog-sprite" src={pokemon.spriteUrl} alt={pokemon.name} />
                  <div className="catalog-info">
                    <span className="catalog-name">
                      #{pokemon.pokedexNumber} {pokemon.name}
                    </span>
                    <div className="catalog-types">
                      {pokemon.types.map((t) => {
                        const style = getTypeStyle(t);
                        return (
                          <span
                            key={t}
                            className="type-badge mini"
                            style={{
                              backgroundColor: style.bg,
                              borderColor: style.border,
                              color: style.text
                            }}
                          >
                            {formatTypeName(t)}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Floating retro tooltip / preview on hover */}
          {hoveredPokemon && (
            <div className="catalog-hover-tooltip" aria-hidden="true">
              <span className="tooltip-name">#{hoveredPokemon.pokedexNumber} {hoveredPokemon.name}</span>
              <span className="tooltip-types">
                {hoveredPokemon.types.map(formatTypeName).join(" / ")}
              </span>
            </div>
          )}
        </div>
      ) : (
        <SynergySuggestions
          activeDetails={activeDetails}
          catalog={results}
          onSelectPokemon={onSelectPokemon}
        />
      )}
    </aside>
  );
}
