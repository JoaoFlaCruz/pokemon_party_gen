import type { Item } from "../types/domain";

export function ItemSelector({ items, value, onChange }: { items: Item[]; value: string | null; onChange(value: string): void }) {
  const selected = items.find((item) => item.id === value);
  return (
    <label className="field">
      Item
      <select aria-label="Item" value={value ?? ""} onChange={(event) => onChange(event.target.value)}>
        <option value="">Nenhum</option>
        {items.map((item) => (
          <option key={item.id} value={item.id}>
            {item.name} - {item.description}
          </option>
        ))}
      </select>
      {selected ? (
        <span className="item-preview">{selected.imageUrl ? <img src={selected.imageUrl} alt={selected.name} /> : <span>Imagem indisponivel</span>}</span>
      ) : null}
    </label>
  );
}
