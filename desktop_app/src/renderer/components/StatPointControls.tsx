import { statKeys, type IVPointAllocation, type StatKey } from "../types/domain";

export function StatPointControls({ ivPoints, onChange }: { ivPoints: IVPointAllocation; onChange(stat: StatKey, value: number): void }) {
  const total = statKeys.reduce((sum, key) => sum + ivPoints[key], 0);
  return (
    <section className="panel compact">
      <h3>IV Points</h3>
      <p>Total {total}/186</p>
      <div className="iv-grid">
        {statKeys.map((key) => (
          <label key={key}>
            {key}
            <input aria-label={`IV ${key}`} type="number" min={0} max={31} value={ivPoints[key]} onChange={(event) => onChange(key, Number(event.target.value))} />
          </label>
        ))}
      </div>
    </section>
  );
}
