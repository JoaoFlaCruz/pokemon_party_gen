## Why

Automatic six-Pokemon team construction is generative AI behavior and should not be exposed as a deterministic MCP tool. The project should keep data-backed validation and ranking tools, while requiring AI-selected Pokemon candidates to remain scoped to the Pokemon Champions library.

## What Changes

- **BREAKING**: Remove `build_pokemon_team` from the MCP tool surface so clients cannot call it through `tools/list` or `tools/call`.
- Inactivate the team-builder wrapper and dispatch path, including schema registration and presentation/executor exposure.
- Update team-building documentation so AI agents assemble teams themselves using validated project data, not a dedicated team construction tool.
- Require AI-facing Pokemon candidate selection to use Pokemon Champions scope; the `rank_pokemon` MCP tool must not allow AI callers to disable Champions filtering.
- Keep existing lower-level PokeAPI-backed validation and ranking behavior available for agents that need candidate data.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `team-builder-tool`: remove the public MCP team-builder contract and update team-building documentation away from `build_pokemon_team`.
- `champions-dex-selection`: change AI-facing ranking behavior so Champions-scoped candidate selection is mandatory instead of optional.

## Impact

- Affected MCP code: `mcp_server/src/mcp/server.py`, `mcp_server/src/mcp/tools/__init__.py`, and `mcp_server/src/mcp/tools/team_builder_tool.py`.
- Affected application code: `mcp_server/src/application/use_cases/build_team.py` may become unused and should be removed or made non-public if no longer referenced.
- Affected tests: MCP tool listing, dispatch, validation, and team-builder tests must be updated or removed to match the inactive tool.
- Affected docs: `docs/architecture.md`, `docs/agentic-team-pattern.md`, and `docs/agentic-team-flow.md` must stop directing agents to use `build_pokemon_team` and must state that AI-selected additions use Champions-only candidate data.
- No new external dependencies are expected.
