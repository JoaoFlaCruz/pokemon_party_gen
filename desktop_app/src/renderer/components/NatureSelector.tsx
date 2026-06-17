import type { Nature } from "../types/domain";

export function NatureSelector({ natures, value, onChange }: { natures: Nature[]; value: string | null; onChange(value: string): void }) {
  return (
    <label className="field">
      Natureza
      <select aria-label="Natureza" value={value ?? ""} onChange={(event) => onChange(event.target.value)}>
        <option value="">Selecione</option>
        {natures.map((nature) => (
          <option key={nature.id} value={nature.id}>
            {nature.name} bonus {nature.bonusStat ?? "-"} onus {nature.onusStat ?? "-"}
          </option>
        ))}
      </select>
    </label>
  );
}
