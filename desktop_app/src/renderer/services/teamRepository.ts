import { savedTeams as initialSavedTeams } from "../data/demo-fixtures";
import { CONTRACT_VERSION, serviceResult, statKeys, type Diagnostic, type ServiceResult } from "../types/domain";
import type { SavedTeam, TeamDraft, TeamListPage, TeamSlot } from "../types/app-state";

export type TeamRepository = {
  saveTeam(team: TeamDraft): Promise<ServiceResult<SavedTeam>>;
  listSavedTeams(page: number): Promise<ServiceResult<TeamListPage>>;
  getSavedTeam(teamId: string): Promise<ServiceResult<SavedTeam | null>>;
};

const savedTeams = [...initialSavedTeams];

export function validateSlot(slot: TeamSlot): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];
  const uniqueMoves = new Set(slot.moveIds);
  if (uniqueMoves.size !== slot.moveIds.length) {
    diagnostics.push({ code: "duplicate_moves", message: "A Pokemon cannot have duplicate moves.", field: `slots.${slot.position}.moveIds`, severity: "error" });
  }
  if (slot.moveIds.length > 4) {
    diagnostics.push({ code: "too_many_moves", message: "A Pokemon can have up to four moves.", field: `slots.${slot.position}.moveIds`, severity: "error" });
  }
  const totalIv = statKeys.reduce((total, key) => total + slot.ivPoints[key], 0);
  for (const key of statKeys) {
    if (!Number.isInteger(slot.ivPoints[key]) || slot.ivPoints[key] < 0 || slot.ivPoints[key] > 31) {
      diagnostics.push({ code: "invalid_iv_value", message: "IV points must be integers from 0 to 31 per stat.", field: `slots.${slot.position}.ivPoints.${key}`, severity: "error" });
    }
  }
  if (totalIv > 186) {
    diagnostics.push({ code: "invalid_iv_total", message: "Total IV allocation cannot exceed 186 points.", field: `slots.${slot.position}.ivPoints`, severity: "error" });
  }
  return diagnostics;
}

export const teamRepository: TeamRepository = {
  async saveTeam(team) {
    const diagnostics: Diagnostic[] = [];
    if (!team.name.trim()) {
      diagnostics.push({ code: "missing_team_name", message: "Team name is required.", field: "name", severity: "error" });
    }
    if (team.slots.length !== 6 || new Set(team.slots.map((slot) => slot.position)).size !== 6) {
      diagnostics.push({ code: "invalid_slots", message: "A team must contain six unique ordered slots.", field: "slots", severity: "error" });
    }
    diagnostics.push(...team.slots.flatMap(validateSlot));
    if (diagnostics.some((diagnostic) => diagnostic.severity === "error")) {
      return serviceResult({ id: "", name: team.name, slots: team.slots, savedAt: "", contractVersion: CONTRACT_VERSION }, diagnostics);
    }
    const saved: SavedTeam = {
      id: `team-${savedTeams.length + 1}`,
      name: team.name,
      slots: team.slots.map((slot) => ({ ...slot, ivPoints: { ...slot.ivPoints }, moveIds: [...slot.moveIds] })),
      savedAt: new Date().toISOString(),
      contractVersion: CONTRACT_VERSION
    };
    savedTeams.unshift(saved);
    return serviceResult(saved);
  },

  async listSavedTeams(page) {
    const pageSize = 3 as const;
    const totalPages = Math.max(1, Math.ceil(savedTeams.length / pageSize));
    const safePage = Math.min(Math.max(1, page), totalPages);
    const start = (safePage - 1) * pageSize;
    const results = savedTeams.slice(start, start + pageSize);
    const diagnostics: Diagnostic[] = results.some((team) => team.contractVersion !== CONTRACT_VERSION)
      ? [{ code: "contract_version_mismatch", message: "Saved team was created with a different fixture contract version.", severity: "warning" }]
      : [];
    return serviceResult({ results, page: safePage, pageSize, totalTeams: savedTeams.length, totalPages }, diagnostics);
  },

  async getSavedTeam(teamId) {
    const found = savedTeams.find((team) => team.id === teamId) ?? null;
    return serviceResult(found, found ? [] : [{ code: "not_found", message: "Saved team not found.", severity: "error" }]);
  }
};
