## 1. Inactivate Team Builder MCP Tool

- [x] 1.1 Remove `TEAM_BUILDER_TOOL` and `execute_team_builder_tool` imports from `mcp_server/src/mcp/server.py`.
- [x] 1.2 Remove `build_pokemon_team` from the MCP `TOOLS` registry and initialization instructions.
- [x] 1.3 Remove `TEAM_BUILDER_TOOL` and `execute_team_builder_tool` lazy exports from `mcp_server/src/mcp/tools/__init__.py`.
- [x] 1.4 Delete or quarantine `mcp_server/src/mcp/tools/team_builder_tool.py` so it is no longer a public AI tool wrapper.
- [x] 1.5 Delete or quarantine `mcp_server/src/application/use_cases/build_team.py` if no remaining runtime or test import requires it.

## 2. Force Champions-Only AI Candidate Ranking

- [x] 2.1 Remove the `champions_only` property from the public `rank_pokemon` MCP input schema.
- [x] 2.2 Update `execute_pokemon_ranking_tool` so MCP calls always pass `champions_only=True` to the ranker.
- [x] 2.3 Keep ranking output and presentation explicit that Champions scope is active.
- [x] 2.4 Preserve any non-MCP CLI or lower-level ranking behavior only where it does not create an AI-facing escape hatch.

## 3. Tests

- [x] 3.1 Update MCP tool listing tests to assert `build_pokemon_team` is absent.
- [x] 3.2 Update MCP dispatch tests to assert calls to `build_pokemon_team` return the unknown-tool validation error.
- [x] 3.3 Remove or rewrite team-builder wrapper tests that depend on the inactive MCP tool.
- [x] 3.4 Update ranking tool tests to assert `champions_only` is not in the schema and the executor calls the ranker with `True`.
- [x] 3.5 Remove or update application `build_team` tests if the use case module is deleted or made non-public.

## 4. Documentation

- [x] 4.1 Update `docs/architecture.md` to remove `build_pokemon_team`, `team_builder_tool.py`, and `build_team.py` from the active architecture and MCP dispatch docs.
- [x] 4.2 Update `docs/agentic-team-pattern.md` so AI team assembly uses lower-level validated tools and always chooses AI-added Pokemon from Champions-scoped candidates.
- [x] 4.3 Update `docs/agentic-team-flow.md` to remove the `build_pokemon_team` call model and describe bounded validation with remaining tools.
- [x] 4.4 Ensure docs clearly distinguish user-selected Pokemon from AI-selected additions and preserve user-selected Pokemon as fixed choices.

## 5. Verification

- [x] 5.1 Run `rg "build_pokemon_team|TEAM_BUILDER_TOOL|execute_team_builder_tool|team_builder_tool|build_team" mcp_server/src mcp_server/tests docs` and confirm only intentional historical or removed references remain.
- [x] 5.2 Run `python3 -m unittest mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers`.
- [x] 5.3 Run `openspec status --change "remove-team-builder-tool-enforce-champions-only"` and confirm the change is apply-ready.
