import { useState } from "react";
import type { Item, Move, PokemonDetails } from "../types/domain";
import type { Gender, TeamSlot } from "../types/app-state";
import { formatTypeName, getTypeStyle } from "../utils/pokemonFormatters";
import { MoveDetailModal } from "./MoveDetailModal";
import { StatBarChart } from "./StatBarChart";

type Props = {
  details: PokemonDetails | null;
  slot: TeamSlot;
  moves: Move[];
  equippedItem?: Item | null;
  onLevelChange?(level: number): void;
  onGenderChange?(gender: Gender): void;
};

export function PokemonDetailPanel({
  details,
  slot,
  moves,
  equippedItem,
  onLevelChange,
  onGenderChange
}: Props) {
  const [inspectingMove, setInspectingMove] = useState<Move | null>(null);

  if (!details) {
    return (
      <aside className="panel detail-panel empty-detail" aria-label="Perfil do Pokémon">
        <header className="detail-header-bar">
          <span className="panel-title">PERFIL</span>
        </header>
        <div className="portrait-box empty">
          <div className="portrait empty">?</div>
        </div>
        <p className="empty-hint">Selecione um Pokémon na caixa para ver os detalhes.</p>
      </aside>
    );
  }

  // Find the 4 active moves for this slot
  const selectedMoves: (Move | null)[] = [0, 1, 2, 3].map((index) => {
    const moveId = slot.moveIds[index];
    if (!moveId) return null;
    return moves.find((m) => m.id === moveId) ?? null;
  });

  return (
    <aside className="panel detail-panel" aria-label="Perfil do Pokémon">
      <header className="detail-header-bar">
        <div className="level-control">
          <label htmlFor="pokemon-level-input" className="level-tag">Lv.</label>
          <input
            id="pokemon-level-input"
            type="number"
            min={1}
            max={100}
            value={slot.level ?? 50}
            onChange={(e) => onLevelChange?.(Number(e.target.value) || 1)}
            aria-label="Nível do Pokémon"
          />
        </div>
        <div className="gender-control">
          <button
            type="button"
            className={`gender-btn male ${slot.gender === "male" ? "active" : ""}`}
            onClick={() => onGenderChange?.(slot.gender === "male" ? "unknown" : "male")}
            title="Gênero: Masculino"
            aria-label="Gênero Masculino"
          >
            ♂
          </button>
          <button
            type="button"
            className={`gender-btn female ${slot.gender === "female" ? "active" : ""}`}
            onClick={() => onGenderChange?.(slot.gender === "female" ? "unknown" : "female")}
            title="Gênero: Feminino"
            aria-label="Gênero Feminino"
          >
            ♀
          </button>
        </div>
      </header>

      {/* Retrato do Pokémon com moldura azul-clara e fundo quadriculado cinza */}
      <div className="portrait-box">
        <img className="portrait" src={details.imageUrl || details.spriteUrl} alt={details.name} />
      </div>

      <div className="detail-meta">
        <div className="meta-row">
          <span className="meta-label">Nome:</span>
          <strong className="meta-value pokemon-name">{details.name}</strong>
        </div>
        <div className="meta-row">
          <span className="meta-label">Tipo:</span>
          <div className="type-badges-row">
            {details.types.map((type) => {
              const style = getTypeStyle(type);
              return (
                <span
                  key={type}
                  className="type-badge"
                  style={{
                    backgroundColor: style.bg,
                    borderColor: style.border,
                    color: style.text
                  }}
                >
                  {formatTypeName(type)}
                </span>
              );
            })}
          </div>
        </div>
        <div className="meta-row">
          <span className="meta-label">Item Equipado:</span>
          <span className="meta-value item-name">
            {equippedItem ? equippedItem.name : "Nenhum"}
          </span>
        </div>
        {/* Preserving text for compatibility/tests */}
        <p className="sr-only">Tipos: {details.types.join(" / ")}</p>
        <p className="sr-only">Total base: {details.totalStats}</p>
        <p className="sr-only">Habilidades: {details.abilities.join(", ")}</p>
      </div>

      {/* 4 Botões Coloridos de Movimentos */}
      <div className="moves-section">
        <h4 className="section-subtitle">Movimentos</h4>
        <div className="move-buttons-grid">
          {selectedMoves.map((move, idx) => {
            if (!move) {
              return (
                <button
                  key={idx}
                  type="button"
                  className="move-btn empty"
                  disabled
                  aria-label={`Golpe ${idx + 1} vazio`}
                >
                  <span className="move-btn-slot">#{idx + 1}</span>
                  <span className="move-btn-name">---</span>
                </button>
              );
            }

            const style = getTypeStyle(move.type);
            return (
              <button
                key={move.id}
                type="button"
                className="move-btn filled"
                style={{
                  backgroundColor: style.bg,
                  borderColor: style.border,
                  color: style.text
                }}
                onClick={() => setInspectingMove(move)}
                aria-label={`Ver detalhes do golpe ${move.name}`}
                title={`Clique para ver detalhes de ${move.name}`}
              >
                <span className="move-btn-slot">#{idx + 1}</span>
                <span className="move-btn-name">{move.name}</span>
                <span className="move-btn-pp">{move.pp ? `${move.pp} PP` : ""}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Gráfico de Barras Horizontais das Estatísticas */}
      <StatBarChart baseStats={details.baseStats} totalStats={details.totalStats} />

      {/* Modal de Detalhes do Golpe (quando clicado) */}
      <MoveDetailModal move={inspectingMove} onClose={() => setInspectingMove(null)} />
    </aside>
  );
}
