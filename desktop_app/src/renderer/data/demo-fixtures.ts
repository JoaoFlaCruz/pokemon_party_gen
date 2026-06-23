import { emptyIvPoints, type Item, type Move, type Nature, type PokemonDetails, type PokemonSummary } from "../types/domain";
import type { SavedTeam, TeamDraft, TeamSlot } from "../types/app-state";

export const fixtureSourceNote =
  "Demo fixture copied from PokeAPI-compatible public species/pokemon/move/item/nature fields for frontend validation only.";

const sprite = (id: number) => `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png`;
const artwork = (id: number) =>
  `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${id}.png`;

export const pokemonDetails: PokemonDetails[] = [
  {
    id: 1,
    name: "bulbasaur",
    pokedexNumber: 1,
    types: ["grass", "poison"],
    spriteUrl: sprite(1),
    imageUrl: artwork(1),
    baseStats: { hp: 45, attack: 49, defense: 49, specialAttack: 65, specialDefense: 65, speed: 45 },
    totalStats: 318,
    abilities: ["overgrow", "chlorophyll"],
    moveIds: ["tackle", "vine-whip", "growl", "razor-leaf"],
    description: "A strange seed was planted on its back at birth.",
    sourceNote: fixtureSourceNote
  },
  {
    id: 4,
    name: "charmander",
    pokedexNumber: 4,
    types: ["fire"],
    spriteUrl: sprite(4),
    imageUrl: artwork(4),
    baseStats: { hp: 39, attack: 52, defense: 43, specialAttack: 60, specialDefense: 50, speed: 65 },
    totalStats: 309,
    abilities: ["blaze", "solar-power"],
    moveIds: ["scratch", "ember", "smokescreen", "flamethrower"],
    description: "The flame on its tail shows the strength of its life force.",
    sourceNote: fixtureSourceNote
  },
  {
    id: 7,
    name: "squirtle",
    pokedexNumber: 7,
    types: ["water"],
    spriteUrl: sprite(7),
    imageUrl: artwork(7),
    baseStats: { hp: 44, attack: 48, defense: 65, specialAttack: 50, specialDefense: 64, speed: 43 },
    totalStats: 314,
    abilities: ["torrent", "rain-dish"],
    moveIds: ["tackle", "water-gun", "withdraw", "bubble"],
    description: "After birth, its back swells and hardens into a shell.",
    sourceNote: fixtureSourceNote
  },
  {
    id: 25,
    name: "pikachu",
    pokedexNumber: 25,
    types: ["electric"],
    spriteUrl: sprite(25),
    imageUrl: artwork(25),
    baseStats: { hp: 35, attack: 55, defense: 40, specialAttack: 50, specialDefense: 50, speed: 90 },
    totalStats: 320,
    abilities: ["static", "lightning-rod"],
    moveIds: ["quick-attack", "thunder-shock", "thunder-wave", "iron-tail"],
    description: "When it is angered, it releases electric power from its cheeks.",
    sourceNote: fixtureSourceNote
  },
  {
    id: 95,
    name: "onix",
    pokedexNumber: 95,
    types: ["rock", "ground"],
    spriteUrl: sprite(95),
    imageUrl: artwork(95),
    baseStats: { hp: 35, attack: 45, defense: 160, specialAttack: 30, specialDefense: 45, speed: 70 },
    totalStats: 385,
    abilities: ["rock-head", "sturdy"],
    moveIds: ["tackle", "rock-throw", "harden", "dig"],
    description: "As it grows, the stone portions of its body harden.",
    sourceNote: fixtureSourceNote
  },
  {
    id: 131,
    name: "lapras",
    pokedexNumber: 131,
    types: ["water", "ice"],
    spriteUrl: sprite(131),
    imageUrl: artwork(131),
    baseStats: { hp: 130, attack: 85, defense: 80, specialAttack: 85, specialDefense: 95, speed: 60 },
    totalStats: 535,
    abilities: ["water-absorb", "shell-armor"],
    moveIds: ["water-gun", "ice-beam", "sing", "body-slam"],
    description: "A gentle Pokemon that carries people across the sea.",
    sourceNote: fixtureSourceNote
  },
  {
    id: 999,
    name: "missingno-demo",
    pokedexNumber: 999,
    types: ["normal"],
    spriteUrl: sprite(0),
    imageUrl: artwork(0),
    baseStats: { hp: 0, attack: 0, defense: 0, specialAttack: 0, specialDefense: 0, speed: 0 },
    totalStats: 0,
    abilities: [],
    moveIds: [],
    description: "",
    sourceNote: "Diagnostic-only fixture with intentionally missing details."
  }
];

export const pokemonSummaries: PokemonSummary[] = pokemonDetails.map(({ baseStats, totalStats, abilities, moveIds, imageUrl, description, ...summary }) => summary);

export const moves: Move[] = [
  { id: "tackle", name: "Tackle", type: "normal", power: 40, pp: 35, damageClass: "physical", description: "A physical attack in which the user charges.", sourceNote: fixtureSourceNote },
  { id: "vine-whip", name: "Vine Whip", type: "grass", power: 45, pp: 25, damageClass: "physical", description: "The target is struck with slender vines.", sourceNote: fixtureSourceNote },
  { id: "growl", name: "Growl", type: "normal", power: null, pp: 40, damageClass: "status", description: "The user growls to lower the target's Attack.", sourceNote: fixtureSourceNote },
  { id: "razor-leaf", name: "Razor Leaf", type: "grass", power: 55, pp: 25, damageClass: "physical", description: "Sharp-edged leaves are launched.", sourceNote: fixtureSourceNote },
  { id: "scratch", name: "Scratch", type: "normal", power: 40, pp: 35, damageClass: "physical", description: "Hard pointed claws rake the target.", sourceNote: fixtureSourceNote },
  { id: "ember", name: "Ember", type: "fire", power: 40, pp: 25, damageClass: "special", description: "A small flame is launched at the target.", sourceNote: fixtureSourceNote },
  { id: "smokescreen", name: "Smokescreen", type: "normal", power: null, pp: 20, damageClass: "status", description: "Lowers the target's accuracy.", sourceNote: fixtureSourceNote },
  { id: "flamethrower", name: "Flamethrower", type: "fire", power: 90, pp: 15, damageClass: "special", description: "The target is scorched with intense fire.", sourceNote: fixtureSourceNote },
  { id: "water-gun", name: "Water Gun", type: "water", power: 40, pp: 25, damageClass: "special", description: "The target is blasted with water.", sourceNote: fixtureSourceNote },
  { id: "withdraw", name: "Withdraw", type: "water", power: null, pp: 40, damageClass: "status", description: "The user withdraws to raise Defense.", sourceNote: fixtureSourceNote },
  { id: "bubble", name: "Bubble", type: "water", power: 40, pp: 30, damageClass: "special", description: "Bubbles are sprayed at the target.", sourceNote: fixtureSourceNote },
  { id: "quick-attack", name: "Quick Attack", type: "normal", power: 40, pp: 30, damageClass: "physical", description: "The user attacks with blinding speed.", sourceNote: fixtureSourceNote },
  { id: "thunder-shock", name: "Thunder Shock", type: "electric", power: 40, pp: 30, damageClass: "special", description: "An electric shock is launched.", sourceNote: fixtureSourceNote },
  { id: "thunder-wave", name: "Thunder Wave", type: "electric", power: null, pp: 20, damageClass: "status", description: "A weak electric charge paralyzes the target.", sourceNote: fixtureSourceNote },
  { id: "iron-tail", name: "Iron Tail", type: "steel", power: 100, pp: 15, damageClass: "physical", description: "The target is slammed with a steel-hard tail.", sourceNote: fixtureSourceNote },
  { id: "rock-throw", name: "Rock Throw", type: "rock", power: 50, pp: 15, damageClass: "physical", description: "A small rock is hurled at the target.", sourceNote: fixtureSourceNote },
  { id: "harden", name: "Harden", type: "normal", power: null, pp: 30, damageClass: "status", description: "The user stiffens to raise Defense.", sourceNote: fixtureSourceNote },
  { id: "dig", name: "Dig", type: "ground", power: 80, pp: 10, damageClass: "physical", description: "The user digs then attacks on the next turn.", sourceNote: fixtureSourceNote },
  { id: "ice-beam", name: "Ice Beam", type: "ice", power: 90, pp: 10, damageClass: "special", description: "An icy beam is fired at the target.", sourceNote: fixtureSourceNote },
  { id: "sing", name: "Sing", type: "normal", power: null, pp: 15, damageClass: "status", description: "A soothing song may make the target sleep.", sourceNote: fixtureSourceNote },
  { id: "body-slam", name: "Body Slam", type: "normal", power: 85, pp: 15, damageClass: "physical", description: "The user drops its full body onto the target.", sourceNote: fixtureSourceNote }
];

export const natures: Nature[] = [
  { id: "hardy", name: "Hardy", bonusStat: null, onusStat: null, description: "Neutral nature with no stat adjustment.", sourceNote: fixtureSourceNote },
  { id: "adamant", name: "Adamant", bonusStat: "attack", onusStat: "specialAttack", description: "Raises Attack and lowers Special Attack.", sourceNote: fixtureSourceNote },
  { id: "modest", name: "Modest", bonusStat: "specialAttack", onusStat: "attack", description: "Raises Special Attack and lowers Attack.", sourceNote: fixtureSourceNote },
  { id: "bold", name: "Bold", bonusStat: "defense", onusStat: "attack", description: "Raises Defense and lowers Attack.", sourceNote: fixtureSourceNote },
  { id: "timid", name: "Timid", bonusStat: "speed", onusStat: "attack", description: "Raises Speed and lowers Attack.", sourceNote: fixtureSourceNote }
];

export const items: Item[] = [
  { id: "leftovers", name: "Leftovers", description: "A held item that gradually restores HP.", imageUrl: "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/leftovers.png", sourceNote: fixtureSourceNote },
  { id: "oran-berry", name: "Oran Berry", description: "A berry that restores a small amount of HP.", imageUrl: "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/oran-berry.png", sourceNote: fixtureSourceNote },
  { id: "charcoal", name: "Charcoal", description: "A held item that strengthens Fire-type moves.", imageUrl: "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/charcoal.png", sourceNote: fixtureSourceNote },
  { id: "mystic-water", name: "Mystic Water", description: "A held item that strengthens Water-type moves.", imageUrl: "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/mystic-water.png", sourceNote: fixtureSourceNote },
  { id: "demo-missing-image", name: "Demo Missing Image", description: "Diagnostic item with no image reference.", imageUrl: null, sourceNote: "Diagnostic-only fixture for placeholder validation." }
];

export function createEmptySlot(position: number): TeamSlot {
  return { position, pokemonId: null, level: 100, gender: "unknown", natureId: null, itemId: null, ivPoints: emptyIvPoints(), moveIds: [] };
}

export function createDefaultDraft(): TeamDraft {
  return { id: "draft-1", name: "Time 1", updatedAt: new Date(0).toISOString(), slots: [1, 2, 3, 4, 5, 6].map(createEmptySlot) };
}

function savedTeam(id: string, name: string, pokemonIds: number[]): SavedTeam {
  const draft = createDefaultDraft();
  return {
    id,
    name,
    savedAt: new Date(2026, 0, Number(id.replace("team-", ""))).toISOString(),
    contractVersion: "fixture-1",
    slots: draft.slots.map((slot, index) => ({ ...slot, pokemonId: pokemonIds[index] ?? null }))
  };
}

export const savedTeams: SavedTeam[] = [
  savedTeam("team-1", "Kanto Balance", [1, 4, 7, 25, 95, 131]),
  savedTeam("team-2", "Water Core", [7, 131, 1]),
  savedTeam("team-3", "Speed Check", [25, 4, 1]),
  savedTeam("team-4", "Rock Anchor", [95, 7, 25])
];
