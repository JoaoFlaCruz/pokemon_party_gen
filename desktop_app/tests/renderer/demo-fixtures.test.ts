import { describe, expect, it } from "vitest";
import { fixtureSourceNote, items, moves, natures, pokemonDetails, pokemonSummaries, savedTeams } from "../../src/renderer/data/demo-fixtures";

describe("demo fixtures", () => {
  it("provide required fixture counts and type variety", () => {
    expect(pokemonSummaries.length).toBeGreaterThanOrEqual(6);
    expect(pokemonDetails.length).toBeGreaterThanOrEqual(6);
    expect(moves.length).toBeGreaterThanOrEqual(8);
    expect(natures.length).toBeGreaterThanOrEqual(5);
    expect(items.length).toBeGreaterThanOrEqual(5);
    expect(savedTeams.length).toBeGreaterThanOrEqual(4);
    expect(pokemonSummaries.some((pokemon) => pokemon.types.length === 1)).toBe(true);
    expect(pokemonSummaries.some((pokemon) => pokemon.types.length === 2)).toBe(true);
  });

  it("include source notes and diagnostic fixtures", () => {
    expect(fixtureSourceNote).toContain("PokeAPI-compatible");
    expect(pokemonDetails.every((pokemon) => pokemon.sourceNote.length > 0)).toBe(true);
    expect(moves.every((move) => move.sourceNote.length > 0)).toBe(true);
    expect(items.some((item) => item.imageUrl === null)).toBe(true);
  });
});
