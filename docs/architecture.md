# Project Architecture

This project provides Python utilities for querying a PokeAPI-compatible API, ranking Pokemon and moves, building Pokemon teams, and exposing that functionality through MCP tools for agents.

## Structure

```text
desktop_app/
    main.js
    index.html
    styles.css
    renderer.js
mcp_server/
    src/
        main.py
        config/
            env.py
        mcp/
            server.py
            tools/
                banned_pokemon_tool.py
                item_tool.py
                pokemon_moveset_tool.py
                pokemon_ranking_tool.py
                team_builder_tool.py
                type_relations_tool.py
                __init__.py
        application/
            api_server.py
            use_cases/
                build_team.py
                rank_pokemon.py
                rank_moveset.py
            dtos/
        domain/
            entities/
            repositories/
            services/
        infrastructure/
            pokeapi/
                pokemon_fetcher.py
                pokemon_moves_fetcher.py
                item_fetcher.py
                type_relations_fetcher.py
            database/
                migrations/
            repositories/
        shared/
            errors/
            logger/
            validation/
    tests/
        application/
            use_cases/
                test_build_team.py
                test_rankings.py
        infrastructure/
            pokeapi/
                test_fetchers.py
        mcp/
            tools/
                test_tools.py
        manual/
            test_fetch_calls.py
```

## Configuration

`mcp_server/src/config/env.py` loads environment variables from a root `.env` file without overriding values that are already defined in the environment.

Supported variables:

- `POKEAPI_BASE_URL`: API base URL. Default: `http://127.0.0.1:8000/api/v2/`.
- `POKEAPI_TIMEOUT`: HTTP call timeout. Default: `30.0`.
- `POKEAPI_MAX_WORKERS`: default number of parallel workers. Default: `12`.
- `BANNED_POKEMON_DB_PATH`: SQLite database path for Pokemon banned from `rank_pokemon`. Default: `banned_pokemon.sqlite3` in the project root.
- `POKEAPI_HTTP_PORT`: host HTTP port used by the root `docker-compose.yml` to expose PokeAPI through Nginx. Default: `8000`.
- `HASURA_HTTP_PORT`: host HTTP port used by the root `docker-compose.yml` to expose Hasura. Default: `8081`.

## Docker Environment

The project root contains a `Dockerfile` for an interactive Codex CLI terminal and a `docker-compose.yml` that includes the internal compose file from `pokeapi/` instead of duplicating its services. The include uses `pokeapi/docker-compose.yml` and `docker/pokeapi-compose.override.yml`; the override keeps PokeAPI services in the subproject compose, adjusts published ports, and uses the local build for the `app` image. The root compose adds only the one-shot `pokeapi-setup` service, which uses the same PokeAPI image, mounts `pokeapi/` at `/code` to access CSV data, and runs migrations plus `build_all()` when the database has not been populated yet.

The `codex` container mounts the project at `/workspace`, copies `docker/codex/config.toml` to `CODEX_HOME/config.toml` on each startup in the writable `codex_home` volume, and registers the `pokemon_tools` MCP server pointing to `python3 -m mcp_server.src.mcp.server`. The service command is `codex --dangerously-bypass-approvals-and-sandbox`, opening the chatbot in the terminal. The `codex_home` volume preserves login state and workspace trust between runs, while the Codex configuration is reapplied from `docker/codex/config.toml` to keep container behavior stable. The service uses `network_mode: host` to allow callbacks on `localhost` during login.

Inside the container, Codex starts with `--dangerously-bypass-approvals-and-sandbox`; it also loads `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, and the `pokemon_tools` MCP uses `default_tools_approval_mode = "approve"`. This policy removes approval prompts for commands, file edits, and MCP tool usage inside Docker without changing the host Codex configuration outside the `codex_home` volume.

Because `codex` uses the host network, MCP accesses PokeAPI through the published host port:

```text
POKEAPI_BASE_URL=http://127.0.0.1:8000/api/v2/
```

To start the full environment, including migration and data loading through the internal PokeAPI flow:

```bash
docker compose up
```

The `app` and `codex` services depend on `pokeapi-setup`, so compose initializes data before starting the API and opening the chatbot. To open only the interactive Codex terminal after the services are ready, use:

```bash
docker compose run --rm codex
```

After that, PokeAPI is available on the host at `http://localhost:8000/api/v2/` by default. Always use Docker Compose V2 (`docker compose`, with a space). Avoid `docker-compose` v1, which can fail with `KeyError: ContainerConfig` on current Docker versions.

## Fetch Layer

`mcp_server/src/infrastructure/pokeapi/` contains the HTTP clients. This layer knows the external API and returns structured data to the business rules.

`PokemonFetcher` fetches Pokemon and their stats. It also calls `pokemon-species/{name}` to exclude legendary species from ranking and `pokemon-form/{name}` to exclude forms marked as `is_battle_only=true`, which represent temporary or battle-restricted forms and should not be selected as resolved PvP team members. Accepted Pokemon include `is_battle_only=false` and preserve `is_mega`, `base_pokemon`, and `required_item` when those metadata exist and the item can be validated through `item/{name}`. It accepts filters by:

- type, up to two types;
- ability;
- learned move.

When filters are combined, the result is the intersection of Pokemon found by each filter. Pokemon details are then fetched in parallel with `ThreadPoolExecutor`.

`PokemonMovesFetcher` fetches one Pokemon by name or ID and enriches each learned move with details from `move/{name}/`. Move details are also fetched in parallel.

`ItemFetcher` lists general items through `item/?limit={limit}&offset={offset}` and enriches each result with details from `item/{name}/`. The response includes pagination (`count`, `next`, `previous`, `limit`, `offset`) and item fields such as `cost`, `fling_power`, `fling_effect`, `attributes`, `category`, `effect_entries`, `flavor_text_entries`, and `sprites`.

`TypeRelationsFetcher` fetches one type by name or ID through `type/{name}/` and normalizes `damage_relations` into two perspectives: `offensive`, with `super_effective_against`, `weak_against`, and `no_effect_against`; and `defensive`, with `weak_to`, `resists`, and `immune_to`. The response also preserves `raw_damage_relations`.

## Rule Layer

`mcp_server/src/application/use_cases/` contains ranking logic, deterministic team-building logic, and CLI entry points when a module has one.

`build_team.py` builds a structured response for six-Pokemon teams from user choices, optional strategies, and ranked candidates. It normalizes input, removes duplicates while preserving the first occurrence, applies the six-user-choice limit, validates Pokemon through an injectable PokeAPI-compatible source, and completes remaining slots with ranked candidates deterministically. The response includes `team_size`, `is_complete`, `user_requested`, `team_structure`, `team`, `analysis`, and `pending`. User Pokemon receive `source=user` and `locked=true`; AI-selected Pokemon receive `source=ai`, `locked=false`, `reason`, `role`, and `replaces_gap`. If data cannot be validated, the uncertainty is recorded in `pending` instead of inventing stats, types, moves, abilities, or items.

`rank_pokemon.py` ranks non-legendary Pokemon that are not marked as `is_battle_only`, using a base score formed by:

```text
hp + defense + special-defense + selected offensive stat
```

The offensive stat can be:

- `auto`: choose `attack` or `special-attack`, whichever is higher for each Pokemon;
- `attack`: force physical attack;
- `special-attack`: force special attack.

Optionally, `priority_stat` can choose a stat to receive a `1.4` multiplier in the score. Accepted values are `hp`, `attack`, `defense`, `special-attack`, `special-defense`, and `speed`. When the prioritized stat is not already in the base score, it becomes part of the calculation.

`speed_mode` controls how speed participates in ranking:

- `ignore`: keep the previous behavior and ignore `speed`;
- `high`: add `speed` to the calculation, favoring fast Pokemon;
- `low`: add `255 - speed` to the calculation, favoring slow Pokemon.

`rank_moveset.py` ranks moves for one Pokemon. It first chooses the Pokemon's best offensive stat:

- `attack` selects `physical` moves;
- `special-attack` selects `special` moves.

Offensive moves in the selected category are ordered by:

```text
accuracy * 1.4 + power
```

Ties use, in order, higher accuracy, higher power, and move name. `status` moves are not ranked and are appended to the end of the result.

## Tool Layer

`mcp_server/src/mcp/tools/` exposes project functionality to agents.

`banned_pokemon_tool.py` defines the `ban_pokemon` tool, validates `id` and `name`, creates the SQLite table `banned_pokemon (id, name)` when needed, and registers the Pokemon in the exclusion database configured by `BANNED_POKEMON_DB_PATH`. The operation is idempotent for existing rows with the same `id` or `name`.

`item_tool.py` defines the `list_items` tool, validates `limit` and `offset`, calls `ItemFetcher`, and returns a general item listing with concise presentation text for AI consumption. The presentation includes category, cost, attributes, and an item description from `effect_entries` or `flavor_text_entries`, preferring English text when available.

`type_relations_tool.py` defines the `get_type_relations` tool, validates `type`, calls `TypeRelationsFetcher`, and returns offensive and defensive type relations in structured and textual formats.

`pokemon_ranking_tool.py` defines the `rank_pokemon` tool, validates optional type filters, `offense_stat`, `priority_stat`, `speed_mode`, and `head_size`, calls `rank_pokemon.py`, and returns a structured ranking with presentation text. Results already exclude legendary species and `is_battle_only` forms. After ranking, the tool also reads the SQLite database configured by `BANNED_POKEMON_DB_PATH` and removes any Pokemon registered in the `banned_pokemon` table, with columns `id` and `name`. If the database file does not exist, no additional filter is applied.

`team_builder_tool.py` defines the `build_pokemon_team` tool, validates `pokemon`, `aces`, `primary_strategy`, and `complementary_strategy`, calls `build_team.py`, and returns a structured team proposal. The tool preserves user-provided Pokemon as fixed members when validated, completes open slots with ranked candidates, separates the team into `primary` and `complementary` trios, marks two aces when possible, and declares pending issues for missing data, conflicts, or insufficient candidates.

`pokemon_moveset_tool.py` defines the `rank_pokemon_moveset` tool, validates arguments, calls the ranking rule, and returns:

- `tool_name`;
- `input`;
- `data`, with the structured result;
- `presentation`, with concise summary text.

`mcp_server/src/mcp/server.py` implements a minimal MCP stdio server with support for:

- `initialize`;
- `ping`;
- `tools/list`;
- `tools/call`.

The `tools/call` request dispatches by tool name and supports `ban_pokemon`, `build_pokemon_team`, `get_type_relations`, `list_items`, `rank_pokemon`, and `rank_pokemon_moveset`, returning textual content and `structuredContent`.

## Tests

Main unit tests are located in:

- `mcp_server/tests/application/use_cases/test_build_team.py`: tests deterministic team-building with fakes, without HTTP.
- `mcp_server/tests/application/use_cases/test_rankings.py`: tests ranking rules with fakes, without HTTP.
- `mcp_server/tests/mcp/tools/test_tools.py`: tests tool schemas, formatting, validation, and basic MCP behavior.
- `mcp_server/tests/infrastructure/pokeapi/test_fetchers.py`: tests fetcher data assembly without real HTTP.

`mcp_server/tests/manual/test_fetch_calls.py` is a manual check to run only when a local PokeAPI is active and populated.

Recommended unit test command:

```bash
python3 -m unittest mcp_server.tests.application.use_cases.test_build_team mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers
```

## Main Flow

```text
CLI or MCP/tool (`build_pokemon_team`, `get_type_relations`, `list_items`, `rank_pokemon`, or `rank_pokemon_moveset`)
    -> mcp_server/src/application/use_cases/ or mcp_server/src/infrastructure/pokeapi/
        -> PokeAPI REST
        -> ranking rule/adaptation
    -> structured response and/or textual presentation

CLI or MCP/tool (`ban_pokemon`)
    -> mcp_server/src/mcp/tools/banned_pokemon_tool.py
        -> SQLite `banned_pokemon`
    -> structured response and textual presentation
```

## Agentic Team Flow

`docs/agentic-team-flow.md` defines five agents for team assembly:

- Agent A: collects Pokemon, move, general item, and type-relation data.
- Agent B: builds a playable proposal with strategy, movesets, abilities, stat distribution, and items when data has been validated.
- Agent E: selects candidates to fill open slots or correct gaps before and after validation stages.
- Agent C: validates team rules, duplicates, items, and strategic cohesion.
- Agent D: audits types, speeds, offensive and defensive stats, roles, weaknesses, and gaps.

That flow follows `docs/agentic-team-flow.pdf` and should be used together with `docs/agentic-team-pattern.md` when an AI needs to complete a six-Pokemon team from user choices and strategy. The workflow includes reflection checkpoints after the initial team draft, strategic validation, balance audit, and before the final response, using `accept`, `refine`, `ask_user`, or `stop_with_pending` decisions to keep refinement bounded. The `build_pokemon_team` tool is the deterministic MCP implementation of that contract: it does not replace final human or agentic analysis, but it provides a validated, structured, and traceable base for agents.

## Desktop App & HTTP Bridge

To support a visual, interactive desktop workflow, the project includes:

- **HTTP API Bridge (`mcp_server/src/application/api_server.py`)**: A lightweight HTTP JSON server built using Python's standard library `http.server`. It runs on port `8002` and acts as a bridge between the Electron client and the internal Python use cases (`build_pokemon_team`, `rank_pokemon`, `rank_pokemon_moveset`, etc.), supporting CORS for local calls.
- **Electron Desktop App (`desktop_app/`)**: A cross-platform desktop UI built with Electron, HTML5, CSS3, and JavaScript. It connects to the API bridge, providing autocomplete search, visual primary/complementary trio cards, ace indicators, bottom sheets for moveset details, and type resistance grids.

## Maintenance Principles

- Keep HTTP calls restricted to `mcp_server/src/infrastructure/pokeapi/`.
- When adding a fetcher, export it in `mcp_server/src/infrastructure/pokeapi/__init__.py` and cover data assembly with tests that do not require real HTTP.
- Keep ranking and team-building rules in `mcp_server/src/application/use_cases/`, testable with fakes.
- Keep agent/MCP wrappers in `mcp_server/src/mcp/tools/` and routing in `mcp_server/src/mcp/server.py`.
- When adding a tool, register its schema, executor, presentation, MCP routing, and tests.
- When changing rules, response contracts, arguments, environment variables, or execution flow, update this documentation.
