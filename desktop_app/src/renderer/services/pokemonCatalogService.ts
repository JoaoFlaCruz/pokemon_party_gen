import { moves, pokemonDetails, pokemonSummaries } from "../data/demo-fixtures";
import { serviceResult, type Diagnostic, type Move, type PokemonDetails, type PokemonFilters, type PokemonSummary, type ServiceResult } from "../types/domain";

export type PokemonCatalogService = {
  listPokemon(filters: PokemonFilters): Promise<ServiceResult<PokemonSummary[]>>;
  getPokemonDetails(pokemonId: number): Promise<ServiceResult<PokemonDetails | null>>;
  listMovesForPokemon(pokemonId: number): Promise<ServiceResult<Move[]>>;
};

function matchesFilters(pokemon: PokemonSummary, filters: PokemonFilters): boolean {
  const name = filters.name?.trim().toLowerCase();
  return (
    (!name || pokemon.name.includes(name)) &&
    (!filters.pokedexNumber || pokemon.pokedexNumber === filters.pokedexNumber) &&
    (!filters.typeA || pokemon.types[0] === filters.typeA) &&
    (!filters.typeB || pokemon.types[1] === filters.typeB)
  );
}

export const pokemonCatalogService: PokemonCatalogService = {
  async listPokemon(filters) {
    const data = pokemonSummaries
      .filter((pokemon) => matchesFilters(pokemon, filters))
      .sort((a, b) => a.pokedexNumber - b.pokedexNumber);
    return serviceResult(data);
  },

  async getPokemonDetails(pokemonId) {
    const found = pokemonDetails.find((pokemon) => pokemon.id === pokemonId && pokemon.description && pokemon.totalStats > 0) ?? null;
    const diagnostics: Diagnostic[] = found
      ? []
      : [{ code: "missing_pokemon_details", message: "Demo fixture details are unavailable for this Pokemon.", severity: "error", field: "pokemonId" }];
    return serviceResult(found, diagnostics);
  },

  async listMovesForPokemon(pokemonId) {
    const found = pokemonDetails.find((pokemon) => pokemon.id === pokemonId);
    if (!found) {
      return serviceResult([], [{ code: "missing_pokemon_moves", message: "Move fixture data is unavailable for this Pokemon.", severity: "error" }]);
    }
    return serviceResult(moves.filter((move) => found.moveIds.includes(move.id)));
  }
};
