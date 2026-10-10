import type { DamageClass, StatKey } from "../types/domain";

export const TYPE_TRANSLATIONS: Record<string, string> = {
  normal: "Normal",
  fire: "Fogo",
  water: "Água",
  grass: "Grama",
  electric: "Elétrico",
  ice: "Gelo",
  fighting: "Lutador",
  poison: "Venenoso",
  ground: "Terrestre",
  flying: "Voador",
  psychic: "Psíquico",
  bug: "Inseto",
  rock: "Pedra",
  ghost: "Fantasma",
  dragon: "Dragão",
  dark: "Sombrio",
  steel: "Aço",
  fairy: "Fada"
};

export const TYPE_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  normal: { bg: "#A8A878", border: "#6D6D4E", text: "#FFFFFF" },
  fire: { bg: "#F08030", border: "#9C531F", text: "#FFFFFF" },
  water: { bg: "#6890F0", border: "#445E9C", text: "#FFFFFF" },
  grass: { bg: "#78C850", border: "#4E8234", text: "#FFFFFF" },
  electric: { bg: "#F8D030", border: "#A1871F", text: "#1A202C" },
  ice: { bg: "#98D8D8", border: "#638D8D", text: "#1A202C" },
  fighting: { bg: "#C03028", border: "#7D1F1A", text: "#FFFFFF" },
  poison: { bg: "#A040A0", border: "#682A68", text: "#FFFFFF" },
  ground: { bg: "#E0C068", border: "#927D44", text: "#1A202C" },
  flying: { bg: "#A890F0", border: "#6D5E9C", text: "#FFFFFF" },
  psychic: { bg: "#F85888", border: "#A13959", text: "#FFFFFF" },
  bug: { bg: "#A8B820", border: "#6D7815", text: "#FFFFFF" },
  rock: { bg: "#B8A038", border: "#786824", text: "#FFFFFF" },
  ghost: { bg: "#705898", border: "#493963", text: "#FFFFFF" },
  dragon: { bg: "#7038F8", border: "#4924A1", text: "#FFFFFF" },
  dark: { bg: "#705848", border: "#49392F", text: "#FFFFFF" },
  steel: { bg: "#B8B8D0", border: "#787887", text: "#1A202C" },
  fairy: { bg: "#EE99AC", border: "#9B6470", text: "#1A202C" }
};

export const DAMAGE_CLASS_TRANSLATIONS: Record<DamageClass, string> = {
  physical: "Físico",
  special: "Especial",
  status: "Status"
};

export const STAT_TRANSLATIONS: Record<StatKey, string> = {
  hp: "HP",
  attack: "Atk",
  defense: "Def",
  specialAttack: "SpA",
  specialDefense: "SpD",
  speed: "Spe"
};

export const STAT_FULL_NAMES: Record<StatKey, string> = {
  hp: "Pontos de Vida (HP)",
  attack: "Ataque (Atk)",
  defense: "Defesa (Def)",
  specialAttack: "Ataque Especial (SpA)",
  specialDefense: "Defesa Especial (SpD)",
  speed: "Velocidade (Spe)"
};

export function formatTypeName(type: string): string {
  return TYPE_TRANSLATIONS[type.toLowerCase()] ?? type;
}

export function formatDamageClass(damageClass: DamageClass): string {
  return DAMAGE_CLASS_TRANSLATIONS[damageClass] ?? damageClass;
}

export function getTypeStyle(type: string) {
  return TYPE_COLORS[type.toLowerCase()] ?? { bg: "#707070", border: "#404040", text: "#FFFFFF" };
}

