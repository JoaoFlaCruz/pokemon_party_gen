import { statKeys, type Move, type PokemonDetails } from "../types/domain";
import type { TeamSlot } from "../types/app-state";

type Props = {
  details: PokemonDetails | null;
  slot: TeamSlot;
  moves: Move[];
};

export function PokemonDetailPanel({ details, slot, moves }: Props) {
  if (!details) {
    return (
      <aside className="panel detail-panel">
        <h2>Pokemon ativo</h2>
        <div className="portrait empty">?</div>
        <p>Selecione um Pokemon para ver os detalhes.</p>
      </aside>
    );
  }

  return (
    <aside className="panel detail-panel">
      <h2>{details.name}</h2>
      <img className="portrait" src={details.imageUrl} alt={details.name} />
      <p>Tipos: {details.types.join(" / ")}</p>
      <p>Total base: {details.totalStats}</p>
      <p>Habilidades: {details.abilities.join(", ")}</p>
      <dl className="stats">
        {statKeys.map((key) => (
          <div key={key}>
            <dt>{key}</dt>
            <dd>{details.baseStats[key]}</dd>
          </div>
        ))}
      </dl>
      <p>{details.description}</p>
      <p className="source-note">{details.sourceNote}</p>
      <h3>Golpes escolhidos</h3>
      <ul>
        {slot.moveIds.length ? slot.moveIds.map((id) => <li key={id}>{moves.find((move) => move.id === id)?.name ?? id}</li>) : <li>Nenhum golpe selecionado</li>}
      </ul>
    </aside>
  );
}
