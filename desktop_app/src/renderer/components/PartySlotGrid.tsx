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
    <section className="party-grid" aria-label="Party slots">
      {slots.map((slot) => {
        const pokemon = slot.pokemonId ? pokemonById.get(slot.pokemonId) : null;
        return (
          <button
            key={slot.position}
            className={`party-slot ${slot.position === activeSlotPosition ? "selected" : ""}`}
            onClick={() => onSelect(slot.position)}
            aria-label={`Slot ${slot.position}`}
          >
            <span className="slot-number">#{slot.position}</span>
            {pokemon ? <img src={pokemon.spriteUrl} alt={pokemon.name} /> : <span className="empty-sprite">-</span>}
            <strong>{pokemon?.name ?? "Vazio"}</strong>
          </button>
        );
      })}
    </section>
  );
}
