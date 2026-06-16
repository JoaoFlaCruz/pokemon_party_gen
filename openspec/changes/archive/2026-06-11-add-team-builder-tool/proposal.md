## Why

The project already has data and ranking tools, plus documented rules for assembling six-Pokemon teams, but there is no MCP tool that orchestrates those rules into a structured team-building workflow. Adding a team-builder tool gives agents a single contract for preserving user choices, completing two complementary trios, and surfacing validation gaps without inventing Pokemon data.

## What Changes

- Add a new MCP tool that accepts user-selected Pokemon and optional strategy constraints, then returns a six-Pokemon team plan.
- Preserve user-selected Pokemon as fixed members and clearly distinguish AI-selected additions.
- Structure the output as two trios of three Pokemon, each with its own ace and strategy.
- Use existing PokeAPI-backed ranking, moveset, item, and type-relation capabilities for data gathering and candidate validation.
- Report pending validation issues when Pokemon data cannot be found or the requested constraints cannot be satisfied.
- Add unit tests for schema validation, tool execution, orchestration behavior, and MCP dispatch.
- Update architecture and team-building documentation to describe the new tool contract and flow.

## Capabilities

### New Capabilities

- `team-builder-tool`: Defines the MCP contract and behavior for building a complete six-Pokemon team from user-selected Pokemon, strategies, constraints, and validated PokeAPI-compatible data.

### Modified Capabilities

- None.

## Impact

- Affected code:
  - `mcp_server/src/mcp/tools/`
  - `mcp_server/src/mcp/server.py`
  - `mcp_server/src/application/use_cases/`
  - existing PokeAPI fetchers and ranking use cases through injected dependencies
- Affected tests:
  - `mcp_server/tests/mcp/tools/test_tools.py`
  - `mcp_server/tests/application/use_cases/test_rankings.py` or new use-case tests for team orchestration
- Affected docs:
  - `docs/architecture.md`
  - `docs/agentic-team-pattern.md`
  - potentially `docs/agentic-team-flow.md`
- No external dependency changes are expected.
