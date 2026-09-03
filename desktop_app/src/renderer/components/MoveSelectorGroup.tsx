import type { Move } from "../types/domain";

type Props = {
  availableMoves: Move[];
  selectedMoveIds: string[];
  onMoveChange(index: number, moveId: string): void;
};

export function MoveSelectorGroup({ availableMoves, selectedMoveIds, onMoveChange }: Props) {
  return (
    <section className="panel compact move-group-panel">
      <h3>Golpes</h3>
      <div className="moves-grid">
        {[0, 1, 2, 3].map((index) => {
          const selected = selectedMoveIds[index] ?? "";
          const options = availableMoves.filter((move) => !selectedMoveIds.includes(move.id) || move.id === selected);
          const selectedMove = availableMoves.find((move) => move.id === selected);
          return (
            <label key={index} className="move-slot-field">
              Golpe {index + 1}
              <select value={selected} title={selectedMove?.description ?? "Selecione um golpe"} onChange={(event) => onMoveChange(index, event.target.value)}>
                <option value="">---</option>
                {options.map((move) => (
                  <option key={move.id} value={move.id}>
                    {move.name} - {move.type} - {move.damageClass}
                  </option>
                ))}
              </select>
              {selectedMove ? <small className="move-desc">{selectedMove.description}</small> : null}
            </label>
          );
        })}
      </div>
    </section>
  );
}
