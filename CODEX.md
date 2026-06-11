# CODEX

This file defines build and maintenance rules for Codex agents working on this project.

## Project Objective

The project is a set of Python utilities for querying a PokeAPI-compatible API, calculating Pokemon and move rankings, building teams, and exposing the functionality through MCP tools.

## Expected Architecture

Preserve separation of responsibilities:

- `mcp_server/src/config/env.py`: configuration and `.env` loading.
- `mcp_server/src/infrastructure/pokeapi/`: HTTP access and adaptation of PokeAPI responses.
- `mcp_server/src/application/use_cases/`: business rules, ranking, team-building logic, and CLIs.
- `mcp_server/src/mcp/tools/`: AI tool wrappers and MCP server. Each tool must have schema, executor, and textual presentation when applicable.
- `mcp_server/tests/application/use_cases/`: unit tests for rules.
- `mcp_server/tests/mcp/tools/`: unit tests for tools and MCP behavior.
- `mcp_server/tests/infrastructure/pokeapi/`: unit tests for fetcher data assembly.
- `mcp_server/tests/manual/`: manual calls against the local API.

New implementations must stay in the appropriate layer. Do not mix ranking rules with HTTP and do not place API logic inside MCP wrappers.

## Current Features

- Fetch Pokemon by type, ability, and learned move.
- Fetch all moves learned by one Pokemon and enrich each move with details.
- Fetch general item data and enrich each item with its characteristics.
- Fetch effectiveness, resistance, and immunity relations between Pokemon types.
- Rank Pokemon by defensive stats plus a selected offensive stat, excluding legendary species and forms marked `is_battle_only=true`.
- Rank one Pokemon moveset according to the best offensive stat.
- Build a deterministic six-Pokemon team proposal with two trios and pending issues.
- Expose `build_pokemon_team`, `get_type_relations`, `list_items`, `rank_pokemon`, `rank_pokemon_moveset`, and `ban_pokemon` through MCP tool wrappers and the MCP stdio server.

## Agentic Rules

- For requests to build a six-Pokemon team from N desired Pokemon, follow `docs/agentic-team-pattern.md`.
- Preserve user choices as fixed team members and clearly distinguish user-selected Pokemon from AI-selected Pokemon.
- When completing open slots, use explicit criteria for coverage, roles, and gaps; do not invent Pokemon data.
- Use the local OpenSpec skills in `.codex/skills/` naturally when the user's intent matches an OpenSpec workflow, even if the skill is not named explicitly.
- Use `openspec-explore` for exploration, requirement discovery, problem investigation, or approach comparison before a change.
- Use `openspec-propose` when the user asks to define, specify, plan, or propose a new change.
- Use `openspec-apply-change` when the user asks to implement, continue, or work through an existing OpenSpec change.
- Use `openspec-sync-specs` when the user asks to sync delta specs into main specs without archiving.
- Use `openspec-archive-change` when the user asks to finalize, complete, or archive an implemented OpenSpec change.

## Implementation Rules

- Use standard Python and preserve the existing simple style.
- Prefer pure functions for ranking and team-building rules.
- Inject fetchers or use protocols/fakes in tests when a rule does not require real HTTP.
- Use `ThreadPoolExecutor` only in the fetch layer when there are independent calls.
- When creating new fetchers, export them in `mcp_server/src/infrastructure/pokeapi/__init__.py` and keep output JSON-serializable.
- Preserve structured responses as JSON-serializable dictionaries.
- Validate public arguments in wrappers and CLIs.
- When creating a new tool, register it in MCP for `tools/list` and `tools/call`.
- Do not invent Pokemon data; query a PokeAPI-compatible source when real data is needed.
- In Pokemon ranking, exclude species with `is_legendary=true` and forms with `is_battle_only=true`, because those forms are not selectable as resolved PvP members.

## Required Documentation

Any new implementation or behavior change must update project documentation.

Update `docs/architecture.md` when changing any of these points:

- folder or module structure;
- input or output contracts;
- ranking rules;
- environment variables;
- run or test commands;
- MCP tools or schemas;
- external dependencies;
- data flow between layers.

Update `docs/agentic-team-pattern.md` when changing team-building rules, team response format, suggested roles, or AI Pokemon selection criteria.

Update `docs/agentic-team-flow.md` when changing the agentic workflow or the 1-to-5-call operating model.

If a change is small and does not alter behavior or architecture, explicitly state in the final summary that documentation was reviewed and did not require changes.

## Tests

Before finalizing code changes, run when possible:

```bash
python3 -m unittest mcp_server.tests.application.use_cases.test_build_team mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers
```

For fetchers, `mcp_server/tests/manual/test_fetch_calls.py` depends on an active and populated local PokeAPI. Do not treat that file as an automatic unit test.

## Change Checklist

- Did the change stay in the correct layer?
- Is the response contract still JSON-serializable?
- Do new or changed rules have unit tests?
- Was `docs/architecture.md` updated when necessary?
- Does MCP behavior remain compatible with `tools/list` and `tools/call`?
