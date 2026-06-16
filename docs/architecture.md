# Project Architecture

This project provides Python utilities for querying a PokeAPI-compatible API, ranking Pokemon and moves, and exposing that functionality through MCP tools for agents.

## Structure

```text
mcp_server/
    src/
        main.py
        config/
            env.py
        mcp/
            server.py
            tools/
                banned_pokemon_tool.py
                champions_legality_tool.py
                item_tool.py
                pokemon_moveset_tool.py
                pokemon_ranking_tool.py
                type_relations_tool.py
                __init__.py
        application/
            use_cases/
                champions_legality.py
                champions_strategy.py
                rank_pokemon.py
                rank_moveset.py
            dtos/
        domain/
            entities/
            repositories/
            services/
        infrastructure/
            pokeapi/
                champions_dex_fetcher.py
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

`ChampionsDexFetcher` fetches the Pokemon Champions library membership from `pokedex/champions/`, falling back to `pokedex/36/` for PokeAPI-compatible servers that only resolve the numeric Pokédex id. It reads `pokemon_entries[].pokemon_species.name` and returns a normalized species-name set. This keeps Champions membership data-backed by the configured PokeAPI source instead of a hard-coded list.

`PokemonFetcher` fetches Pokemon and their stats. It also calls `pokemon-species/{name}` to exclude legendary species from ranking and `pokemon-form/{name}` to exclude forms marked as `is_battle_only=true`, which represent temporary or battle-restricted forms and should not be selected as resolved PvP team members. Accepted Pokemon include `is_battle_only=false`, a complete base stat set (`hp`, `attack`, `defense`, `special-attack`, `special-defense`, and `speed`), and preserve `is_mega`, `base_pokemon`, and `required_item` when those metadata exist and the item can be validated through `item/{name}`. Pokemon whose configured data source omits required stats are excluded from ranking candidates instead of being scored with fabricated zero values. Pokemon detail lookup for legality and strategy tools also exposes species, types, abilities, complete stats, form metadata, Champions membership, completeness state, and missing fields. It accepts filters by:

- type, up to two types;
- ability;
- learned move.

When filters are combined, the result is the intersection of Pokemon found by each filter. When Champions scope is enabled, the candidate pool is also intersected with species from the Champions Pokédex before details are fetched, and returned summaries include `champions_dex` membership metadata. Pokemon details are then fetched in parallel with `ThreadPoolExecutor`.

`PokemonMovesFetcher` fetches one Pokemon by name or ID and enriches each learned move with details from `move/{name}/`. Move details are also fetched in parallel. The moveset ranking rule requires the Pokemon to have `attack` and `special-attack` stats plus at least one learned move; missing required stats or an empty move list is reported as a data failure instead of producing an unsupported moveset.

`ItemFetcher` lists general items through `item/?limit={limit}&offset={offset}` and enriches each result with details from `item/{name}/`. The response includes pagination (`count`, `next`, `previous`, `limit`, `offset`) and item fields such as `cost`, `fling_power`, `fling_effect`, `attributes`, `category`, `effect_entries`, `flavor_text_entries`, and `sprites`.

`TypeRelationsFetcher` fetches one type by name or ID through `type/{name}/` and normalizes `damage_relations` into two perspectives: `offensive`, with `super_effective_against`, `weak_against`, and `no_effect_against`; and `defensive`, with `weak_to`, `resists`, and `immune_to`. The response also preserves `raw_damage_relations`.

## Rule Layer

`mcp_server/src/application/use_cases/` contains ranking logic and CLI entry points when a module has one. Full six-Pokemon team construction is handled by the AI workflow described in `docs/agentic-team-pattern.md` and `docs/agentic-team-flow.md`, using validated lower-level tool data rather than a dedicated team-builder use case.

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

Pokemon with incomplete base stats are excluded before scoring. This keeps incomplete API payloads, such as Champions members with no populated stats, out of AI candidate lists.

`rank_moveset.py` ranks moves for one Pokemon. It first chooses the Pokemon's best offensive stat:

- `attack` selects `physical` moves;
- `special-attack` selects `special` moves.

Offensive moves in the selected category are ordered by:

```text
accuracy * 1.4 + power
```

Ties use, in order, higher accuracy, higher power, and move name. `status` moves are not ranked and are appended to the end of the result.

`champions_legality.py` validates Pokemon, moves, abilities, and items against available Pokemon Champions data. It returns structured facts plus `legal`, `eligible`, `checked_scope`, `diagnostics`, and `blocking` fields. Pokemon, move, and ability legality are based on configured Pokemon and learnset data. Item validation proves item existence and useful item facts when available, but reports `unsupported_validation` for Champions-specific item legality when the configured source does not expose format item rules.

`champions_strategy.py` contains internal Champions-scoped candidate search helpers by predefined role or structured strategy case. These helpers are not exposed as an MCP tool because team strategy, role selection, and candidate synthesis must remain inside the agentic A-F workflow. When the AI needs a strategy case, it should construct that case in the workflow from lower-level facts gathered through ranking, legality, moveset, item, and type-relation tools instead of delegating strategic selection to a public role-search tool. Supported internal role concepts include `rain-setter`, `rain-attacker`, `defensive-pivot`, `ground-check`, `fighting-check`, `fire-check`, `speed-control`, and `win-condition`; internally these roles are built-in cases.

Each role or case uses a bounded search plan before any broad fallback: ability filters such as `drizzle`, `swift-swim`, and `rain-dish`; move filters such as `rain-dance`, `tailwind`, `icy-wind`, `thunder-wave`, and setup moves; type filters for coverage or defensive roles; and stat-profile evidence evaluated against returned Pokemon facts. Candidates from plan queries are merged by normalized identity, only `champions_dex=true` candidates are eligible, and excluded candidates with false or unknown membership are reported. Strategy-search data reports `candidate_count`, `evaluated_count`, `excluded_count`, `partial_results`, `search_plan`, and, for injected cases, `case_name` and normalized `case` metadata. Diagnostics include `strategy_search_timeout`, `strategy_search_budget_exhausted`, `partial_strategy_evidence`, `invalid_strategy_case`, `unsupported_strategy_predicate`, `incomplete_strategy_case`, `source_unavailable`, `incomplete_data`, and `no_eligible_candidates`.

## Tool Layer

`mcp_server/src/mcp/tools/` exposes project functionality to agents.

`banned_pokemon_tool.py` defines the `ban_pokemon` tool, validates `id` and `name`, creates the SQLite table `banned_pokemon (id, name)` when needed, and registers the Pokemon in the exclusion database configured by `BANNED_POKEMON_DB_PATH`. The operation is idempotent for existing rows with the same `id` or `name`.

`champions_legality_tool.py` defines the `validate_champions_legality` tool, validates `entity_type`, `entity`, and optional `pokemon`, calls the Champions legality use case, and returns structured legality facts with diagnostics for missing data, source failures, outside-scope entities, and unsupported validation dimensions.

`item_tool.py` defines the `list_items` tool, validates `limit` and `offset`, calls `ItemFetcher`, and returns a general item listing with structured pagination and item details plus concise presentation text for AI consumption. Structured item entries include category, cost, fling data, attributes, effect entries, flavor text entries, and sprites when available. The presentation includes category, cost, attributes, and an item description from `effect_entries` or `flavor_text_entries`, preferring English text when available.

`type_relations_tool.py` defines the `get_type_relations` tool, validates `type`, calls `TypeRelationsFetcher`, and returns the queried type identity plus offensive and defensive type relations in structured and textual formats.

`pokemon_ranking_tool.py` defines the `rank_pokemon` tool, validates optional type filters, `offense_stat`, `priority_stat`, `speed_mode`, `head_size`, and `champions_only`, calls `rank_pokemon.py`, and returns a structured ranking with presentation text. Structured candidates include identity, stats, selected offensive stat, ranking score details, species metadata when available, and Champions scope metadata. MCP ranking defaults to `champions_only=true`, but callers may explicitly pass `champions_only=false` to rank against the broader configured PokeAPI-compatible source. Results already exclude legendary species and `is_battle_only` forms. After ranking, the tool also reads the SQLite database configured by `BANNED_POKEMON_DB_PATH` and removes any Pokemon registered in the `banned_pokemon` table, with columns `id` and `name`. If the database file does not exist, no additional filter is applied.

`pokemon_moveset_tool.py` defines the `rank_pokemon_moveset` tool, validates arguments, calls the ranking rule, and returns:

- `tool_name`;
- `input`;
- `data`, with the structured result, including Pokemon identity and stats plus move entries with name, category, rank and score when ranked, accuracy, power, damage class, type, PP, priority, and learn metadata when available;
- `presentation`, with concise summary text.

`mcp_server/src/mcp/server.py` implements a minimal MCP stdio server with support for:

- `initialize`;
- `ping`;
- `tools/list`;
- `tools/call`.

The `tools/call` request dispatches by tool name and supports `ban_pokemon`, `get_type_relations`, `list_items`, `rank_pokemon`, `rank_pokemon_moveset`, and `validate_champions_legality`, returning textual content and `structuredContent`. `build_pokemon_team` and `search_champions_strategy` are not active MCP tools; calls with those names use the standard unknown-tool error path.

For data tools used by the agentic team flow, `structuredContent` preserves the full tool result with `tool_name`, `input`, `data`, `presentation`, and `diagnostics`. Agents should consume structured `data` for required Pokemon, move, item, type, and Champions facts; presentation text is a summary and is not the only source for required fields.

## Tests

Main unit tests are located in:

- `mcp_server/tests/application/use_cases/test_rankings.py`: tests ranking rules with fakes, without HTTP.
- `mcp_server/tests/mcp/tools/test_tools.py`: tests tool schemas, formatting, validation, and basic MCP behavior.
- `mcp_server/tests/infrastructure/pokeapi/test_fetchers.py`: tests fetcher data assembly without real HTTP.

`mcp_server/tests/manual/test_fetch_calls.py` is a manual check to run only when a local PokeAPI is active and populated.

Recommended unit test command:

```bash
python3 -m unittest mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers
```

## Main Flow

```text
CLI or MCP/tool (`get_type_relations`, `list_items`, `rank_pokemon`, or `rank_pokemon_moveset`)
    -> mcp_server/src/application/use_cases/ or mcp_server/src/infrastructure/pokeapi/
        -> PokeAPI REST
        -> ranking rule/adaptation
    -> structured response and/or textual presentation

CLI or MCP/tool (`validate_champions_legality`)
    -> mcp_server/src/application/use_cases/champions_legality.py
        -> PokeAPI REST through Pokemon, moves, and item fetchers
        -> Champions membership checks
    -> structured facts, diagnostics, and textual presentation

CLI or MCP/tool (`ban_pokemon`)
    -> mcp_server/src/mcp/tools/banned_pokemon_tool.py
        -> SQLite `banned_pokemon`
    -> structured response and textual presentation
```

## Agentic Team Flow

`docs/agentic-team-flow.md` defines six agents for team assembly:

- Agent A: collects Pokemon, move, general item, and type-relation data.
- Agent B: builds a playable proposal with strategy, roles, abilities, and provisional set details when data has been validated.
- Agent E: selects candidates to fill open slots or correct gaps before and after validation stages.
- Agent C: validates team rules, duplicates, items, and strategic cohesion.
- Agent D: audits types, speeds, offensive and defensive stats, roles, weaknesses, and gaps.
- Agent F: populates final per-Pokemon moves, EVs, nature, item, and usage suggestion after team composition and strategy are stable.

That flow follows `docs/agentic-team-flow.pdf` and should be used together with `docs/agentic-team-pattern.md` when an AI needs to complete a six-Pokemon team from user choices and strategy. The workflow includes reflection checkpoints after the initial team draft, strategic validation, balance audit, Agent F set population, complete-member validation, and before the final response, using `accept`, `refine`, `ask_user`, or `stop_with_pending` decisions to keep refinement bounded. For Champions-only requests, AI-selected additions must be chosen from Champions-scoped candidate data provided by `rank_pokemon` with `champions_only=true`; user-selected Pokemon remain fixed choices and are distinguished from AI additions.

A final Pokemon member is complete only when it includes identity and ownership fields, role, trio, reason, exactly four moves with reasons, EVs with named stat point allocations, nature, item, usage suggestion, notes, and `replaces_gap` for AI selections. The flow must not choose `accept` when a final Pokemon is missing a required field. If a focused lower-level tool call can provide missing Pokemon, move, item, type, or Champions data within the call model, Agent A collects it and Agent F updates the affected set; otherwise the flow stops with `pending` rather than inventing unsupported details.

For Champions-only weather or mechanic-driven requests, such as Archaludon rain, the flow should validate fixed Pokemon and proposed entities with `validate_champions_legality`, then let Agents B and E construct role needs and candidate hypotheses from lower-level factual tools. The agent may use `rank_pokemon` filters, `rank_pokemon_moveset`, `get_type_relations`, `list_items`, and focused legality checks to prove setters, abusers, pivots, coverage, items, and final moves. Structured diagnostics such as `pokemon_not_found`, `outside_champions_scope`, `incomplete_data`, `source_unavailable`, `unsupported_validation`, and `no_eligible_candidates` must be carried into `pending` when they block completion. The workflow must not call a public `search_champions_strategy` shortcut; role selection and strategy composition remain A-F responsibilities.

Archaludon rain completion is covered by unit fakes that include enough Champions-eligible role candidates. A populated local PokeAPI was not manually queried during the bounded strategy-search change; if configured local data lacks Archaludon, rain-setting evidence, role candidates, movesets, items, or Champions membership, the workflow should report the corresponding structured blockers instead of presenting a complete team.

## Maintenance Principles

- Keep HTTP calls restricted to `mcp_server/src/infrastructure/pokeapi/`.
- When adding a fetcher, export it in `mcp_server/src/infrastructure/pokeapi/__init__.py` and cover data assembly with tests that do not require real HTTP.
- Keep ranking rules in `mcp_server/src/application/use_cases/`, testable with fakes.
- Keep agent/MCP wrappers in `mcp_server/src/mcp/tools/` and routing in `mcp_server/src/mcp/server.py`.
- When adding a tool, register its schema, executor, presentation, MCP routing, and tests.
- When changing rules, response contracts, arguments, environment variables, or execution flow, update this documentation.
