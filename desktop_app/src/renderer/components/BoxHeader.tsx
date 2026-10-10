type Props = {
  teamName: string;
  activeTeamIndex: number;
  maxTeams?: number;
  onNameChange(name: string): void;
  onSwitchTeam(nextIndex: number): void;
};

export function BoxHeader({
  teamName,
  activeTeamIndex,
  maxTeams = 10,
  onNameChange,
  onSwitchTeam
}: Props) {
  const canGoPrev = activeTeamIndex > 1;
  const canGoNext = activeTeamIndex < maxTeams;

  return (
    <header className="box-header-banner" aria-label="Cabeçalho da Caixa de Pokémon">
      <button
        type="button"
        className="box-nav-btn prev"
        disabled={!canGoPrev}
        onClick={() => onSwitchTeam(activeTeamIndex - 1)}
        aria-label="Time anterior"
        title="Ir para o time anterior"
      >
        ◀
      </button>

      <div className="box-title-container">
        <span className="box-tree-decor left">🌲🌲</span>
        <label className="box-name-label">
          <input
            className="box-name-input"
            value={teamName}
            onChange={(e) => onNameChange(e.target.value)}
            aria-label="Nome do time"
            placeholder={`Time ${activeTeamIndex}`}
          />
          <span className="box-capacity-tag">(6 PkmN)</span>
        </label>
        <span className="box-tree-decor right">🌲🌲</span>
      </div>

      <button
        type="button"
        className="box-nav-btn next"
        disabled={!canGoNext}
        onClick={() => onSwitchTeam(activeTeamIndex + 1)}
        aria-label="Próximo time"
        title="Ir para o próximo time"
      >
        ▶
      </button>
    </header>
  );
}

