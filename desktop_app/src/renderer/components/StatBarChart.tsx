import { statKeys, type BaseStats, type StatKey } from "../types/domain";
import { STAT_FULL_NAMES, STAT_TRANSLATIONS } from "../utils/pokemonFormatters";

type Props = {
  baseStats: BaseStats;
  totalStats?: number;
};

const STAT_COLORS: Record<StatKey, string> = {
  hp: "#48bb78",
  attack: "#f56565",
  defense: "#ed8936",
  specialAttack: "#4299e1",
  specialDefense: "#9f7aea",
  speed: "#38b2ac"
};

const MAX_STAT_BAR = 160;

export function StatBarChart({ baseStats, totalStats }: Props) {
  return (
    <div className="stat-bar-chart" aria-label="Estatísticas do Pokémon">
      <div className="stat-chart-header">
        <h4>Estatísticas Base</h4>
        {totalStats !== undefined ? <span className="stat-total">Total: {totalStats}</span> : null}
      </div>
      <div className="stat-bars-container">
        {statKeys.map((key) => {
          const value = baseStats[key] ?? 0;
          const percentage = Math.min(100, Math.round((value / MAX_STAT_BAR) * 100));
          const color = STAT_COLORS[key] || "#cbd5e0";
          const label = STAT_TRANSLATIONS[key];
          const fullName = STAT_FULL_NAMES[key];

          return (
            <div key={key} className="stat-bar-row" title={`${fullName}: ${value}`}>
              <span className="stat-label">{label}</span>
              <span className="stat-value">{value}</span>
              <div className="stat-track">
                <div
                  className="stat-fill"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: color
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

