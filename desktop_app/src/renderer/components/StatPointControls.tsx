import { statKeys, type IVPointAllocation, type StatKey } from "../types/domain";

export function StatPointControls({ ivPoints, onChange }: { ivPoints: IVPointAllocation; onChange(stat: StatKey, value: number): void }) {
  const total = statKeys.reduce((sum, key) => sum + ivPoints[key], 0);
  return (
    <div className="iv-section">
      <div className="iv-header">
        <h4>IV Points</h4>
        <span>Total {total}/186</span>
      </div>
      <div className="iv-grid">
        {statKeys.map((key) => (
          <label key={key}>
            <span>{key}</span>
            <input aria-label={`IV ${key}`} type="number" min={0} max={31} value={ivPoints[key]} onChange={(event) => onChange(key, Number(event.target.value))} />
          </label>
        ))}
      </div>
    </div>
  );
}
