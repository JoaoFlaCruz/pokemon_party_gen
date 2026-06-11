## Context

The repository currently exposes `build_pokemon_team` through the MCP server, with a wrapper in `mcp_server/src/mcp/tools/team_builder_tool.py` and deterministic assembly logic in `mcp_server/src/application/use_cases/build_team.py`. Documentation also tells agents to use that tool as the primary path for six-Pokemon team construction.

The requested direction is that full team construction belongs to the generative AI workflow, not to a dedicated MCP tool. Project tools should provide validated facts, rankings, item data, moveset ranking, and type relations. When the AI selects Pokemon candidates, it must use the Pokemon Champions library scope.

## Goals / Non-Goals

**Goals:**

- Remove `build_pokemon_team` from MCP discovery and dispatch.
- Inactivate or remove the team-builder wrapper and unused deterministic team assembly entry points.
- Update tests so `tools/list` and `tools/call` enforce the smaller tool surface.
- Update documentation to describe AI-driven team assembly using lower-level validation tools.
- Make `rank_pokemon` Champions-scoped for AI callers without an input escape hatch to unrestricted candidates.

**Non-Goals:**

- Do not remove lower-level Pokemon ranking, move ranking, item listing, type relation, or ban tools.
- Do not introduce a replacement team-builder tool under another name.
- Do not hard-code Pokemon Champions membership; continue using the configured PokeAPI-compatible Champions Pokédex source.
- Do not change manual/local PokeAPI setup.

## Decisions

1. Remove the MCP registration instead of leaving a hidden callable tool.

   `build_pokemon_team` should be absent from `TOOLS`, `tools/list`, initialization instructions, and `tools/call` dispatch. A call by name should return the existing unknown-tool validation error. This provides an unambiguous inactivation boundary for AI clients.

   Alternative considered: keep the tool registered but return an inactive/deprecated error. That still advertises a generative assembly affordance to agents, which conflicts with the requested behavior.

2. Remove the `champions_only` AI input from `rank_pokemon` rather than only defaulting it to `true`.

   The current schema exposes `champions_only` as a boolean with default `true`, which allows an AI caller to set it to `false`. The MCP wrapper should force `champions_only=True` internally and omit that property from the public schema and structured input.

   Alternative considered: reject `champions_only=false` while keeping the schema property. That is more backward compatible, but it still invites clients to try disabling the required scope. Omitting the property better communicates the contract.

3. Keep Champions discovery data-backed.

   Ranking should continue to rely on `PokemonFetcher(... champions_only=True ...)` and `ChampionsDexFetcher` so membership remains defined by the configured PokeAPI-compatible source.

   Alternative considered: embed a static Champions list for reliability. That would risk stale or invented Pokemon data and conflicts with existing repository rules.

4. Update documentation as part of the behavioral change.

   `docs/architecture.md`, `docs/agentic-team-pattern.md`, and `docs/agentic-team-flow.md` currently point agents at `build_pokemon_team`. They must describe team assembly as an AI process that uses `rank_pokemon` with forced Champions scope and supporting tools for validation.

## Risks / Trade-offs

- Existing MCP clients calling `build_pokemon_team` will break → This is an intentional breaking change; unknown-tool behavior and release notes/docs should make the migration clear.
- Removing the deterministic team builder reduces repeatability for full teams → Agents can still use ranked, data-backed candidates and must explain their selected additions explicitly.
- Some tests may depend on team-builder helpers → Replace MCP contract tests with absence/error tests and remove application tests only if the application use case is deleted.
- Hidden imports may keep the removed wrapper reachable → Search imports and package lazy exports before finalizing.

## Migration Plan

1. Remove `TEAM_BUILDER_TOOL` and `execute_team_builder_tool` imports from the MCP server and package export paths.
2. Remove `build_pokemon_team` from `TOOLS`, initialization instructions, architecture docs, and team-flow docs.
3. Remove or quarantine `team_builder_tool.py` and `build_team.py` if no code path needs them.
4. Update `rank_pokemon` MCP schema and executor so Champions scope is always true for AI calls.
5. Update tests to assert the tool is absent and `champions_only=false` is unavailable or ignored according to the final implementation.
6. Run the repository unit test command from `AGENTS.md`.

Rollback is to restore the archived change or re-add the MCP registration and schema if a future requirement explicitly reintroduces deterministic team assembly.

## Open Questions

- None blocking. The implementation can choose physical deletion versus leaving non-exported code based on import/test impact, but the MCP behavior must be inactive.
