## 1. PokeAPI Membership Source

- [x] 1.1 Add infrastructure support for fetching Champions Pokédex membership from `pokedex/champions/`, with fallback to `pokedex/36/`.
- [x] 1.2 Parse `pokemon_entries[].pokemon_species.name` into a normalized species-name set and surface fetch failures as explicit exceptions.
- [x] 1.3 Export the new fetcher/helper from `mcp_server/src/infrastructure/pokeapi/__init__.py`.

## 2. Ranking Integration

- [x] 2.1 Extend the Pokemon ranking fetch path to accept a Champions-scope option or allowed-species provider.
- [x] 2.2 Intersect type, ability, move, and all-Pokemon candidate pools with Champions species before scoring.
- [x] 2.3 Include Champions scope metadata in ranking results and tool presentation.
- [x] 2.4 Preserve existing banned-Pokemon filtering after ranking while keeping the response deterministic.

## 3. Team Builder Integration

- [x] 3.1 Update the default team candidate ranker to use Champions-scoped ranking.
- [x] 3.2 Preserve validated user-selected Pokemon even when outside the Champions Pokédex.
- [x] 3.3 Add member metadata and `pending` entries for user-selected Pokemon whose Champions membership is known to be false.
- [x] 3.4 Include team-level metadata indicating AI candidates are constrained to the Pokemon Champions library.

## 4. MCP Tool Contracts

- [x] 4.1 Update `rank_pokemon` schema, executor input/output, and presentation text for Champions library scope.
- [x] 4.2 Update `build_pokemon_team` structured output and presentation text to report Champions scope and out-of-library user choices.
- [x] 4.3 Verify MCP dispatch still returns `content` text and `structuredContent` for both affected tools.

## 5. Tests

- [x] 5.1 Add infrastructure tests for Champions Pokédex membership parsing, identifier lookup, numeric fallback, and fetch failure.
- [x] 5.2 Add ranking tests proving Champions scope filters unrestricted and typed candidate pools.
- [x] 5.3 Add team-builder tests proving AI-selected members come from Champions candidates and user-selected out-of-library members are preserved with pending issues.
- [x] 5.4 Add MCP tool tests for schema/output metadata and presentation text.
- [x] 5.5 Run `python3 -m unittest mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers`.

## 6. Documentation

- [x] 6.1 Update `docs/architecture.md` with the Champions Pokédex data flow and PokeAPI endpoint contract.
- [x] 6.2 Update `docs/agentic-team-pattern.md` to state that AI-selected Pokemon must come from the Pokemon Champions library while user-selected Pokemon remain locked.
- [x] 6.3 Review `docs/agentic-team-flow.md` and update it if the reflection flow needs to mention Champions-scope pending issues.
