# Repository Guidelines

## Project Structure & Module Organization

This workspace contains Python utilities for querying a PokeAPI-compatible API,
ranking Pokemon and moves, and exposing the functionality through MCP tools.

- `mcp_server/src/config/env.py`: environment configuration.
- `mcp_server/src/infrastructure/pokeapi/`: HTTP access and adaptation of PokeAPI responses.
- `mcp_server/src/application/use_cases/`: business rules, ranking logic, and CLIs.
- `mcp_server/src/mcp/tools/`: AI tool wrappers and the MCP stdio server.
- `mcp_server/tests/application/use_cases/`: unit tests for ranking rules.
- `mcp_server/tests/mcp/tools/`: unit tests for tool wrappers and MCP behavior.
- `mcp_server/tests/infrastructure/pokeapi/`: unit tests for fetcher data assembly without real HTTP.
- `mcp_server/tests/manual/`: manual checks against a running local PokeAPI.
- `docs/architecture.md`: architecture, contracts, flow, tools, and test notes.
- `docs/agentic-team-pattern.md`: rules for assembling six-Pokemon teams.
- `docs/agentic-team-flow.md`: agentic workflow and reflection decisions for multi-step team assembly.
- `pokeapi/`: local PokeAPI source used as a compatible API reference/runtime.

## Build, Test, and Development Commands

There is no separate build step for the Python utilities.

- `python3 -m unittest mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers`: run unit tests.
- `python3 -m unittest mcp_server.tests.manual.test_fetch_calls`: run manual fetch checks only when a local PokeAPI is active and populated.
- `rg "identifier" src docs`: search project code and documentation.
- `sed -n '1,200p' docs/architecture.md`: inspect architecture documentation.

The default API base URL is `http://localhost/api/v2/`. Configure runtime behavior
through `.env` or the environment variables documented in `docs/architecture.md`.

## Coding Style & Naming Conventions

Use straightforward Python and preserve the existing simple module style. Keep
responsibilities separated:

- Keep HTTP calls and API response adaptation in `mcp_server/src/infrastructure/pokeapi/`.
- Keep ranking and business rules in `mcp_server/src/application/use_cases/`.
- Keep MCP schemas, validation, presentation text, and dispatch in `mcp_server/src/mcp/tools/`.

Return JSON-serializable dictionaries from public functions and tools. Validate
public arguments in wrappers and CLIs. Prefer pure functions for ranking rules and
use fakes or injected fetchers in tests when HTTP is not required.

## Testing Guidelines

Before finalizing code changes, run:

```bash
python3 -m unittest mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers
```

Do not treat `mcp_server/tests/manual/test_fetch_calls.py` as an automatic unit test; it depends on a
local PokeAPI server and populated data. For fetcher changes, cover data assembly
with tests that do not require real HTTP.

## Documentation Guidelines

Any new implementation or behavior change must update project documentation.
Update `docs/architecture.md` when changing:

- folder or module structure;
- input or output contracts;
- ranking rules;
- environment variables;
- run or test commands;
- MCP tools or schemas;
- external dependencies;
- data flow between layers.

Update `docs/agentic-team-pattern.md` when changing team-building rules,
response format for teams, suggested roles, or AI Pokemon selection criteria.

If a change is small and does not alter behavior or architecture, state in the
final summary that documentation was reviewed and did not require changes.

## Commit & Pull Request Guidelines

Keep commit subjects concise and scoped to the change, such as `Add type relation
tool tests` or `Adjust moveset ranking`. Pull requests should summarize the
change, list affected modules or tools, describe test coverage, and call out any
manual PokeAPI checks or uncertain data.

## Agent-Specific Instructions

Do not invent Pokemon data. Use the project tools or a PokeAPI-compatible source
when real Pokemon data is needed. For requests to assemble a team of 6 Pokemon,
follow `docs/agentic-team-pattern.md`; for multi-step team assembly, also follow
`docs/agentic-team-flow.md` and its reflection decisions. Preserve user-selected
Pokemon as fixed members, and clearly distinguish user choices from AI-selected
additions.

Use the local OpenSpec skills in `.codex/skills/` naturally when the user's
intent matches an OpenSpec workflow, even if the user does not name the skill:

- Use `openspec-explore` for exploratory discussion, requirement discovery,
  problem investigation, or comparing possible approaches before a change.
- Use `openspec-propose` when the user asks to define, specify, plan, or propose
  a new change.
- Use `openspec-apply-change` when the user asks to implement, continue, or work
  through an existing OpenSpec change.
- Use `openspec-sync-specs` when the user asks to sync delta specs into the main
  specs without archiving.
- Use `openspec-archive-change` when the user asks to finalize, complete, or
  archive an implemented OpenSpec change.

When adding a tool, register its schema, executor, MCP dispatch, presentation, and
tests. When adding a fetcher, export it from `mcp_server/src/infrastructure/pokeapi/__init__.py`. Keep changes
focused and avoid unrelated formatting churn.
