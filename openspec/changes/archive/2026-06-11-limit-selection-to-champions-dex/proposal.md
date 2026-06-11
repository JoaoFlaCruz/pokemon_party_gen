## Why

The team builder and ranking tools currently select from the general PokeAPI Pokemon pool, which can include Pokemon outside the Pokemon Champions library. The bundled PokeAPI data already exposes a `champions` Pokédex, so selection should be constrained to that validated library instead of relying on undocumented assumptions.

## What Changes

- Add a Champions-dex candidate filter based on the PokeAPI `/api/v2/pokedex/champions/` resource, falling back to numeric id `36` only if needed by the configured compatible API.
- Restrict AI-selected team candidates to Pokemon whose species appears in the Champions Pokédex.
- Expose the same candidate source constraint through the ranking path used by tools so callers can request or observe Champions-scoped results.
- Preserve user-selected Pokemon as fixed choices after normal validation, while reporting when a user-selected Pokemon is outside the Champions library.
- Include Champions-scope metadata in structured tool output and presentation text.

## Capabilities

### New Capabilities

- `champions-dex-selection`: Defines how tools discover and enforce Pokemon Champions library membership for candidate selection.

### Modified Capabilities

- `team-builder-tool`: AI-selected team members must come from the Pokemon Champions library, and outputs must report Champions library scope and out-of-library user choices.

## Impact

- Affected code: `mcp_server/src/infrastructure/pokeapi/`, `mcp_server/src/application/use_cases/rank_pokemon.py`, `mcp_server/src/application/use_cases/build_team.py`, `mcp_server/src/mcp/tools/pokemon_ranking_tool.py`, `mcp_server/src/mcp/tools/team_builder_tool.py`, and related tests.
- Affected API usage: PokeAPI-compatible REST calls add `/api/v2/pokedex/champions/` or `/api/v2/pokedex/36/` to derive allowed species names from `pokemon_entries`.
- Documentation updates: `docs/architecture.md`, `docs/agentic-team-pattern.md`, and OpenSpec specs need to describe the Champions library constraint.
