import type { PokemonSummary } from "../types/domain";
import type { TeamSlot } from "../types/app-state";

type Props = {
  slots: TeamSlot[];
  activeSlotPosition: number;
  pokemonById: Map<number, PokemonSummary>;
  onSelect(position: number): void;
};

export function PartySlotGrid({ slots, activeSlotPosition, pokemonById, onSelect }: Props) {
  return (
    <section className="party-box-storage" aria-label="Party slots">
      <div className="box-grass-field">
        <div className="box-slots-grid">
          {slots.map((slot) => {
            const pokemon = slot.pokemonId ? pokemonById.get(slot.pokemonId) : null;
            const isAce = slot.position === 1;
            const isPartner = slot.position === 2;

            return (
              <button
                key={slot.position}
                type="button"
                className={`party-slot ${slot.position === activeSlotPosition ? "selected" : ""}`}
                onClick={() => onSelect(slot.position)}
                aria-label={`Slot ${slot.position}`}
              >
                <div className="slot-badge-row">
                  <span className="slot-number">#{slot.position}</span>
                  {isAce && (
                    <span className="role-badge ace" title="Ace do 1º Trio" aria-label="Ace">
                      ⭐
                    </span>
                  )}
                  {isPartner && (
                    <span className="role-badge partner" title="2º Pokémon do 1º Trio" aria-label="Parceiro">
                      ❤️
                    </span>
                  )}
                </div>

                <div className="slot-sprite-container">
                  {pokemon ? (
                    <img className="pokemon-menu-sprite" src={pokemon.spriteUrl} alt={pokemon.name} />
                  ) : (
                    <span className="empty-sprite">-</span>
                  )}
                </div>

                <strong className="slot-pokemon-name">{pokemon?.name ?? "Vazio"}</strong>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
