## Context

The project currently exposes MCP tools for ranking Pokemon, ranking movesets, listing items, registering banned Pokemon, and fetching type relations. The documentation already defines how an AI should assemble a complete six-Pokemon team: preserve user-selected Pokemon, complete two trios, identify two aces, avoid invented data, and report uncertainties.

The missing piece is an executable MCP contract that turns those documented rules into a structured response. The implementation should stay consistent with the current architecture: HTTP calls remain in `mcp_server/src/infrastructure/pokeapi/`, business orchestration belongs in `mcp_server/src/application/use_cases/`, and MCP schema, validation, presentation, and dispatch belong in `mcp_server/src/mcp/tools/` and `mcp_server/src/mcp/server.py`.

## Goals / Non-Goals

**Goals:**

- Add a `build_pokemon_team` MCP tool that accepts user-selected Pokemon and optional strategy constraints.
- Preserve user-selected Pokemon as locked entries and clearly identify AI-selected Pokemon.
- Return exactly six team slots when enough validated data is available.
- Structure the team as `primary` and `complementary` trios with distinct strategies and aces.
- Use existing PokeAPI-backed fetchers and ranking use cases to validate names, gather candidate data, and avoid invented Pokemon information.
- Return pending issues instead of fabricating data when validation fails or constraints cannot be satisfied.
- Keep the orchestration testable with fake data providers and no real HTTP in unit tests.

**Non-Goals:**

- Build a full competitive battle simulator.
- Guarantee metagame-optimal teams, EV spreads, natures, or legality across every format.
- Add new external dependencies.
- Replace the existing ranking, moveset, item, type-relation, or banned-Pokemon tools.
- Change PokeAPI data loading or local PokeAPI deployment.

## Decisions

1. Add a pure team-building use case in `mcp_server/src/application/use_cases/`.

   The use case should accept injected collaborators for Pokemon lookup, ranking, moveset checks, and type relation lookups. This keeps the team-building logic independent from MCP and allows tests to cover orchestration without HTTP.

   Alternative considered: implement the workflow directly inside the MCP tool wrapper. That would be faster initially, but it would mix validation, presentation, and business rules in one module and make meaningful unit tests harder.

2. Add a thin `build_pokemon_team` MCP wrapper.

   The wrapper should define JSON schema, validate public arguments, call the use case, and format a concise presentation. It should mirror the current tool pattern used by `rank_pokemon`, `rank_pokemon_moveset`, `list_items`, and `get_type_relations`.

   Alternative considered: expose the feature only as a CLI. The main use case is agent consumption through MCP, so MCP should be the first contract; a CLI can be added later if needed.

3. Validate user-selected Pokemon before completing the team.

   The orchestration should normalize names, remove duplicate user selections while preserving first occurrence, enforce the six-Pokemon limit, and validate requested Pokemon through PokeAPI-compatible data. If a requested Pokemon cannot be validated, it should appear in `pending` and the tool should avoid inventing its stats, types, moves, or role-specific details.

   Alternative considered: keep unknown user Pokemon as normal team members. That conflicts with the repository rule to avoid invented Pokemon data and would make downstream validation unreliable.

4. Complete open slots through ranked candidate groups.

   The first implementation can use deterministic candidate selection based on existing ranking data and declared constraints. It should prefer candidates that fill explicit gaps such as missing second ace, type coverage, defensive resilience, physical/special balance, or speed control. Ties should be deterministic unless a future argument explicitly requests controlled randomness.

   Alternative considered: run a multi-agent loop in code. The documented A-E flow is useful as a conceptual model, but a deterministic use case is simpler to test and safer for an MCP tool contract.

5. Return structured data as the source of truth.

   The MCP result should include `team_size`, `user_requested`, `team_structure`, `team`, `analysis`, and `pending`, matching the documentation. `presentation` should summarize the structured result, but callers should rely on `data` for downstream processing.

   Alternative considered: return only prose. That would be easier to read but would make validation, tests, and agent chaining weaker.

## Risks / Trade-offs

- Candidate quality may be coarse at first because the existing ranker focuses on stats and type filters, not full battle synergy. → Mitigate by returning transparent `reason`, `replaces_gap`, `analysis.risks`, and keeping the scoring logic deterministic and test-covered.
- PokeAPI does not directly encode every competitive rule or item legality nuance. → Mitigate by declaring pending issues and avoiding claims that are not backed by fetched data.
- The tool may require multiple API calls for validation and candidate discovery. → Mitigate by reusing existing max-worker patterns and keeping unit tests on fakes.
- User constraints can be contradictory. → Mitigate by returning pending or blocked statuses rather than silently dropping user choices.
- The team-flow documentation describes multiple agents, while the code will implement a single deterministic orchestration use case. → Mitigate by mapping the A-E responsibilities to internal phases and documenting that the MCP tool is the executable contract.

## Migration Plan

1. Add the use case and tests with fake data providers.
2. Add the MCP tool wrapper and register it in the MCP server.
3. Add tool and dispatch tests.
4. Update architecture and team-building docs.
5. Run the existing unit test suite.

Rollback is straightforward: remove the new tool registration and modules. No data migration is required.

## Open Questions

- Should the first version accept explicit candidate exclusions beyond the existing banned-Pokemon database?
- Should controlled randomness be an argument, or should the first version stay fully deterministic?
- Should held item and moveset suggestions be included in the first implementation or deferred until team member selection is stable?
