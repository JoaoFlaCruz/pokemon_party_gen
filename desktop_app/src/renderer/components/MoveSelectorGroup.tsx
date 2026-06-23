import type { Move } from "../types/domain";

type Props = {
  availableMoves: Move[];
  selectedMoveIds: string[];
  onMoveChange(index: number, moveId: string): void;
};

export function MoveSelectorGroup({ availableMoves, selectedMoveIds, onMoveChange }: Props) {
  return (
    <section className="panel compact">
      <h3>Golpes</h3>
      {[0, 1, 2, 3].map((index) => {
        const selected = selectedMoveIds[index] ?? "";
        const options = availableMoves.filter((move) => !selectedMoveIds.includes(move.id) || move.id === selected);
        const selectedMove = availableMoves.find((move) => move.id === selected);
        return (
          <label key={index}>
            Golpe {index + 1}
            <select value={selected} title={selectedMove?.description ?? "Selecione um golpe"} onChange={(event) => onMoveChange(index, event.target.value)}>
              <option value="">---</option>
              {options.map((move) => (
                <option key={move.id} value={move.id}>
                  {move.name} - {move.type} - {move.damageClass}
                </option>
              ))}
            </select>
            {selectedMove ? <small>{selectedMove.description}</small> : null}
          </label>
        );
      })}
    </section>
  );
}
