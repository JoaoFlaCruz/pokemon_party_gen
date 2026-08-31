import type { PokemonDetails } from "../types/domain";
import { formatTypeName, getTypeStyle } from "../utils/pokemonFormatters";

type Props = {
  details: PokemonDetails | null;
};

export function PokedexEntryBox({ details }: Props) {
  return (
    <section className="pokedex-entry-box" aria-label="Dados da Pokédex">
      <header className="pokedex-box-header">
        <span className="pokedex-title">POKEDEX</span>
        {details ? <span className="pokedex-entry-number">No. {String(details.pokedexNumber).padStart(3, "0")}</span> : null}
      </header>

      <div className="pokedex-box-content bg-checkered-blue">
        {details ? (
          <div className="pokedex-info-body">
            <div className="pokedex-top-info">
              <h3 className="pokedex-species-name">{details.name}</h3>
              <div className="pokedex-types">
                {details.types.map((type) => {
                  const style = getTypeStyle(type);
                  return (
                    <span
                      key={type}
                      className="type-badge small"
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
            <p className="pokedex-flavor-text">{details.description || "Nenhum dado registrado na Pokédex."}</p>
          </div>
        ) : (
          <div className="pokedex-empty-state">
            <p>Selecione um Pokémon na caixa para consultar os dados na Pokédex.</p>
          </div>
        )}
      </div>
    </section>
  );
}

