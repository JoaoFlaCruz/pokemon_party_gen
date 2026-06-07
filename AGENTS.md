# Repository Guidelines

## Project Structure & Module Organization

This workspace contains Python utilities for querying a PokeAPI-compatible API,
ranking Pokemon and moves, and exposing the functionality through MCP tools.

- `src/config.py`: environment configuration.
- `src/fetch/`: HTTP access and adaptation of PokeAPI responses.
- `src/script/`: business rules, ranking logic, and CLIs.
- `src/tool/`: AI tool wrappers and the MCP stdio server.
- `src/test_scripts.py`: unit tests for ranking rules.
- `src/test_tools.py`: unit tests for tool wrappers and MCP behavior.
- `src/test_fetchers.py`: unit tests for fetcher data assembly without real HTTP.
- `src/test_fetch_calls.py`: manual checks against a running local PokeAPI.
- `docs/arquitetura.md`: architecture, contracts, flow, tools, and test notes.
- `docs/padrao-agentico-times.md`: rules for assembling 6-Pokemon teams.
- `pokeapi/`: local PokeAPI source used as a compatible API reference/runtime.

## Build, Test, and Development Commands

There is no separate build step for the Python utilities.

- `python3 -m unittest src.test_scripts src.test_tools src.test_fetchers`: run unit tests.
- `python3 -m unittest src.test_fetch_calls`: run manual fetch checks only when a local PokeAPI is active and populated.
- `rg "identifier" src docs`: search project code and documentation.
- `sed -n '1,200p' docs/arquitetura.md`: inspect architecture documentation.

The default API base URL is `http://localhost/api/v2/`. Configure runtime behavior
through `.env` or the environment variables documented in `docs/arquitetura.md`.

## Coding Style & Naming Conventions

Use straightforward Python and preserve the existing simple module style. Keep
responsibilities separated:

- Keep HTTP calls and API response adaptation in `src/fetch/`.
- Keep ranking and business rules in `src/script/`.
- Keep MCP schemas, validation, presentation text, and dispatch in `src/tool/`.

Return JSON-serializable dictionaries from public functions and tools. Validate
public arguments in wrappers and CLIs. Prefer pure functions for ranking rules and
use fakes or injected fetchers in tests when HTTP is not required.

## Testing Guidelines

Before finalizing code changes, run:

```bash
python3 -m unittest src.test_scripts src.test_tools src.test_fetchers
```

Do not treat `src/test_fetch_calls.py` as an automatic unit test; it depends on a
local PokeAPI server and populated data. For fetcher changes, cover data assembly
with tests that do not require real HTTP.

## Documentation Guidelines

Any new implementation or behavior change must update project documentation.
Update `docs/arquitetura.md` when changing:

- folder or module structure;
- input or output contracts;
- ranking rules;
- environment variables;
- run or test commands;
- MCP tools or schemas;
- external dependencies;
- data flow between layers.

Update `docs/padrao-agentico-times.md` when changing team-building rules,
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
follow `docs/padrao-agentico-times.md`, preserve user-selected Pokemon as fixed
members, and clearly distinguish user choices from AI-selected additions.

When adding a tool, register its schema, executor, MCP dispatch, presentation, and
tests. When adding a fetcher, export it from `src/fetch/__init__.py`. Keep changes
focused and avoid unrelated formatting churn.
