export const CONTRACT_VERSION = "fixture-1" as const;

export type ContractVersion = typeof CONTRACT_VERSION;
export type DiagnosticSeverity = "info" | "warning" | "error";
export type StatKey = "hp" | "attack" | "defense" | "specialAttack" | "specialDefense" | "speed";
export type DamageClass = "physical" | "special" | "status";

export type Diagnostic = {
  code: string;
  message: string;
  field?: string;
  severity: DiagnosticSeverity;
};

export type ServiceResult<T> = {
  data: T;
  diagnostics: Diagnostic[];
  meta: {
    contractVersion: ContractVersion;
  };
};

export type BaseStats = Record<StatKey, number>;
export type IVPointAllocation = Record<StatKey, number>;

export type PokemonSummary = {
  id: number;
  name: string;
  pokedexNumber: number;
  types: string[];
  spriteUrl: string;
  sourceNote: string;
};

export type PokemonDetails = PokemonSummary & {
  baseStats: BaseStats;
  totalStats: number;
  abilities: string[];
  moveIds: string[];
  imageUrl: string;
  description: string;
};

export type Move = {
  id: string;
  name: string;
  type: string;
  power: number | null;
  pp: number | null;
  description: string;
  damageClass: DamageClass;
  sourceNote: string;
};

export type Nature = {
  id: string;
  name: string;
  bonusStat: StatKey | null;
  onusStat: StatKey | null;
  description: string;
  sourceNote: string;
};

export type Item = {
  id: string;
  name: string;
  description: string;
  imageUrl: string | null;
  sourceNote: string;
};

export type PokemonFilters = {
  typeA?: string;
  typeB?: string;
  name?: string;
  pokedexNumber?: number;
};

export const statKeys: StatKey[] = ["hp", "attack", "defense", "specialAttack", "specialDefense", "speed"];

export function emptyIvPoints(): IVPointAllocation {
  return { hp: 0, attack: 0, defense: 0, specialAttack: 0, specialDefense: 0, speed: 0 };
}

export function serviceResult<T>(data: T, diagnostics: Diagnostic[] = []): ServiceResult<T> {
  return { data, diagnostics, meta: { contractVersion: CONTRACT_VERSION } };
}
