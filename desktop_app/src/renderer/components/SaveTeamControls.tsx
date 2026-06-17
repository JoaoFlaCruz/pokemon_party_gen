export function SaveTeamControls({ onSave }: { onSave(): void }) {
  return (
    <div className="save-controls">
      <button className="primary" onClick={onSave}>
        Salvar time
      </button>
    </div>
  );
}
