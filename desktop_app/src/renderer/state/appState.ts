import { createDefaultDraft, savedTeams } from "../data/demo-fixtures";
import { CONTRACT_VERSION, emptyIvPoints, statKeys, type Diagnostic, type StatKey } from "../types/domain";
import type { AppState, AppView, SavedTeam, TeamDraft, TeamSlot } from "../types/app-state";

export type AppAction =
  | { type: "navigate"; view: AppView }
  | { type: "selectSlot"; position: number }
  | { type: "setTeamName"; name: string }
  | { type: "assignPokemon"; pokemonId: number }
  | { type: "setNature"; natureId: string }
  | { type: "setItem"; itemId: string }
  | { type: "setIv"; stat: StatKey; value: number }
  | { type: "setMove"; index: number; moveId: string }
  | { type: "saveTeam"; team: SavedTeam }
  | { type: "setSavedTeamsPage"; page: number }
  | { type: "setDiagnostics"; diagnostics: Diagnostic[] };

export function createInitialState(): AppState {
  return {
    currentView: "team-builder",
    activeSlotPosition: 1,
    draft: createDefaultDraft(),
    savedTeams: savedTeams,
    savedTeamsPage: 1,
    diagnostics: []
  };
}

function updateActiveSlot(draft: TeamDraft, activeSlotPosition: number, updater: (slot: TeamSlot) => TeamSlot): TeamDraft {
  return {
    ...draft,
    updatedAt: new Date().toISOString(),
    slots: draft.slots.map((slot) => (slot.position === activeSlotPosition ? updater(slot) : slot))
  };
}

function validateIv(slot: TeamSlot, stat: StatKey, value: number): Diagnostic[] {
  if (!Number.isInteger(value) || value < 0 || value > 31) {
    return [{ code: "invalid_iv_value", message: "IV points must be integers from 0 to 31 per stat.", field: `ivPoints.${stat}`, severity: "error" }];
  }
  const next = { ...slot.ivPoints, [stat]: value };
  const total = statKeys.reduce((sum, key) => sum + next[key], 0);
  if (total > 186) {
    return [{ code: "invalid_iv_total", message: "Total IV allocation cannot exceed 186 points.", field: "ivPoints", severity: "error" }];
  }
  return [];
}

export function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case "navigate":
      return { ...state, currentView: action.view, diagnostics: [] };
    case "selectSlot":
      return { ...state, activeSlotPosition: action.position, diagnostics: [] };
    case "setTeamName":
      return { ...state, draft: { ...state.draft, name: action.name, updatedAt: new Date().toISOString() } };
    case "assignPokemon":
      return {
        ...state,
        draft: updateActiveSlot(state.draft, state.activeSlotPosition, (slot) => ({
          ...slot,
          pokemonId: action.pokemonId,
          natureId: null,
          itemId: null,
          ivPoints: emptyIvPoints(),
          moveIds: []
        })),
        diagnostics: []
      };
    case "setNature":
      return { ...state, draft: updateActiveSlot(state.draft, state.activeSlotPosition, (slot) => ({ ...slot, natureId: action.natureId })) };
    case "setItem":
      return { ...state, draft: updateActiveSlot(state.draft, state.activeSlotPosition, (slot) => ({ ...slot, itemId: action.itemId })) };
    case "setIv": {
      const slot = state.draft.slots.find((candidate) => candidate.position === state.activeSlotPosition);
      if (!slot) return state;
      const diagnostics = validateIv(slot, action.stat, action.value);
      if (diagnostics.length) return { ...state, diagnostics };
      return {
        ...state,
        diagnostics: [],
        draft: updateActiveSlot(state.draft, state.activeSlotPosition, (candidate) => ({
          ...candidate,
          ivPoints: { ...candidate.ivPoints, [action.stat]: action.value }
        }))
      };
    }
    case "setMove": {
      const slot = state.draft.slots.find((candidate) => candidate.position === state.activeSlotPosition);
      if (!slot) return state;
      const nextMoves = [...slot.moveIds];
      nextMoves[action.index] = action.moveId;
      const compact = nextMoves.filter(Boolean);
      if (new Set(compact).size !== compact.length) {
        return { ...state, diagnostics: [{ code: "duplicate_moves", message: "A Pokemon cannot have duplicate moves.", field: "moveIds", severity: "error" }] };
      }
      return {
        ...state,
        diagnostics: [],
        draft: updateActiveSlot(state.draft, state.activeSlotPosition, (candidate) => ({ ...candidate, moveIds: compact.slice(0, 4) }))
      };
    }
    case "saveTeam":
      return { ...state, savedTeams: [{ ...action.team, contractVersion: action.team.contractVersion || CONTRACT_VERSION }, ...state.savedTeams], diagnostics: [] };
    case "setSavedTeamsPage":
      return { ...state, savedTeamsPage: action.page };
    case "setDiagnostics":
      return { ...state, diagnostics: action.diagnostics };
    default:
      return state;
  }
}
