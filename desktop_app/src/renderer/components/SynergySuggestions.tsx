import { useMemo } from "react";
import type { PokemonDetails, PokemonSummary } from "../types/domain";
import { formatTypeName, getTypeStyle } from "../utils/pokemonFormatters";

type Props = {
  activeDetails: PokemonDetails | null;
  catalog: PokemonSummary[];
  onSelectPokemon(pokemonId: number): void;
};

export function SynergySuggestions({ activeDetails, catalog, onSelectPokemon }: Props) {
  // Generate 3 visual suggestions based on complementary types / available catalog
  const suggestions = useMemo(() => {
    if (!catalog.length || !activeDetails) {
      return [];
    }

    const currentId = activeDetails.id;
    const currentTypes = new Set(activeDetails.types);

    // Prefer Pokemon with different types that complement the active one
    const candidates = catalog.filter((p) => p.id !== currentId && !p.name.includes("missingno"));
    const complementary = candidates.filter((p) => !p.types.some((t) => currentTypes.has(t)));

    const result = complementary.length >= 3 ? complementary.slice(0, 3) : candidates.slice(0, 3);
    return result;
  }, [activeDetails, catalog]);

  return (
    <section className="synergy-section" aria-label="Sugestões de Sinergia">
      <div className="synergy-header-bar">
        <span>Sugestões</span>
      </div>

      <div className="synergy-list">
        {suggestions.length === 0 ? (
          <p className="synergy-empty">Selecione um Pokémon para ver sugestões.</p>
        ) : (
          suggestions.map((pokemon) => (
            <div key={pokemon.id} className="synergy-row">
              <img className="synergy-sprite" src={pokemon.spriteUrl} alt={pokemon.name} />
              <div className="synergy-info">
                <span className="synergy-name">{pokemon.name}</span>
                <div className="synergy-types">
                  {pokemon.types.map((type) => {
                    const style = getTypeStyle(type);
                    return (
                      <span
                        key={type}
                        className="type-badge mini"
                        style={{
                          backgroundColor: style.bg,
                          borderColor: style.border,
                          color: style.text
                        }}
                      >
                        {formatTypeName(type)}
                      </span>
                    );
                  })}
                </div>
              </div>
              <button
                type="button"
                className="synergy-add-btn"
                onClick={() => onSelectPokemon(pokemon.id)}
                title={`Adicionar ${pokemon.name} ao time`}
                aria-label={`Adicionar ${pokemon.name}`}
              >
                +
              </button>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
