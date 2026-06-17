import { describe, expect, it } from "vitest";
import { pokemonCatalogService } from "../../src/renderer/services/pokemonCatalogService";
import { catalogService } from "../../src/renderer/services/catalogService";
import { teamRepository } from "../../src/renderer/services/teamRepository";
import { createDefaultDraft } from "../../src/renderer/data/demo-fixtures";

describe("fixture services", () => {
  it("filters Pokemon and returns ordered results with metadata", async () => {
    const result = await pokemonCatalogService.listPokemon({ typeA: "water" });
    expect(result.meta.contractVersion).toBe("fixture-1");
    expect(result.data.map((pokemon) => pokemon.pokedexNumber)).toEqual([7, 131]);
  });

  it("returns diagnostics for missing Pokemon details", async () => {
    const result = await pokemonCatalogService.getPokemonDetails(999);
    expect(result.data).toBeNull();
    expect(result.diagnostics[0].code).toBe("missing_pokemon_details");
  });

  it("lists natures and items without network access", async () => {
    await expect(catalogService.listNatures()).resolves.toMatchObject({ data: expect.any(Array) });
    const items = await catalogService.listItems("left");
    expect(items.data[0].id).toBe("leftovers");
  });

  it("validates save payload and paginates saved teams", async () => {
    const invalid = createDefaultDraft();
    invalid.name = "";
    const rejected = await teamRepository.saveTeam(invalid);
    expect(rejected.diagnostics.some((diagnostic) => diagnostic.code === "missing_team_name")).toBe(true);

    const page = await teamRepository.listSavedTeams(1);
    expect(page.data.pageSize).toBe(3);
    expect(page.data.results).toHaveLength(3);
  });
});
