import type { Move } from "../types/domain";
import { formatDamageClass, formatTypeName, getTypeStyle } from "../utils/pokemonFormatters";

type Props = {
  move: Move | null;
  onClose(): void;
};

export function MoveDetailModal({ move, onClose }: Props) {
  if (!move) return null;

  const typeStyle = getTypeStyle(move.type);

  return (
    <div className="retro-modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-label="Detalhes do Golpe">
      <div className="retro-modal-card" onClick={(e) => e.stopPropagation()}>
        <header className="retro-modal-header" style={{ backgroundColor: typeStyle.bg, color: typeStyle.text }}>
          <span className="retro-modal-title">{move.name}</span>
          <button className="retro-modal-close" onClick={onClose} aria-label="Fechar">
            ✕
          </button>
        </header>
        <div className="retro-modal-body">
          <div className="move-detail-badges">
            <span
              className="type-badge"
              style={{
                backgroundColor: typeStyle.bg,
                borderColor: typeStyle.border,
                color: typeStyle.text
              }}
            >
              {formatTypeName(move.type)}
            </span>
            <span className={`damage-class-badge ${move.damageClass}`}>
              {formatDamageClass(move.damageClass)}
            </span>
          </div>

          <div className="move-stats-grid">
            <div className="move-stat-box">
              <span className="stat-name">Potência</span>
              <strong className="stat-val">{move.power !== null ? move.power : "---"}</strong>
            </div>
            <div className="move-stat-box">
              <span className="stat-name">Precisão</span>
              <strong className="stat-val">{move.pp !== null ? "100%" : "---"}</strong>
            </div>
            <div className="move-stat-box">
              <span className="stat-name">PP</span>
              <strong className="stat-val">{move.pp !== null ? `${move.pp}/${move.pp}` : "---"}</strong>
            </div>
          </div>

          <div className="move-detail-desc">
            <h4>Descrição</h4>
            <p>{move.description || "Nenhuma descrição detalhada disponível."}</p>
          </div>
        </div>
        <footer className="retro-modal-footer">
          <button className="retro-btn" onClick={onClose}>
            Fechar
          </button>
        </footer>
      </div>
    </div>
  );
}

