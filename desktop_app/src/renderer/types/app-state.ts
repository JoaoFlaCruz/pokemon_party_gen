import type { Diagnostic, IVPointAllocation } from "./domain";

export type AppView = "team-builder" | "saved-teams";
export type Gender = "male" | "female" | "unknown";

export type TeamSlot = {
  position: number;
  pokemonId: number | null;
  level: number;
  gender: Gender;
  natureId: string | null;
  itemId: string | null;
  ivPoints: IVPointAllocation;
  moveIds: string[];
};

export type TeamDraft = {
  id: string;
  name: string;
  slots: TeamSlot[];
  updatedAt: string;
};

export type SavedTeam = {
  id: string;
  name: string;
  slots: TeamSlot[];
  savedAt: string;
  contractVersion: string;
};

export type TeamListPage = {
  results: SavedTeam[];
  page: number;
  pageSize: 3;
  totalTeams: number;
  totalPages: number;
};

export type AppState = {
  currentView: AppView;
  activeSlotPosition: number;
  draft: TeamDraft;
  savedTeams: SavedTeam[];
  savedTeamsPage: number;
  diagnostics: Diagnostic[];
};
