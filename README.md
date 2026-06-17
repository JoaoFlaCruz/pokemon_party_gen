# Pokemon Party Gen

Pokemon Party Gen is a layered desktop product for querying a local
PokeAPI-compatible API, ranking Pokemon and moves, building teams, and exposing
those functions through an Electron desktop app, a Python BFF/API surface, and
MCP tools for Codex.

The root Docker environment starts:

- a local PokeAPI using the internal compose file in `pokeapi/`;
- Postgres, Redis, Nginx, and Hasura for PokeAPI;
- an interactive terminal with Codex CLI;
- the `pokemon_tools` MCP server, pointing to `mcp_server/src/mcp/server.py`;
- a Codex configuration inside the container that avoids approval prompts for sandbox and MCP tool usage.

## Basic Structure

- `.specify/memory/constitution.md`: project governance for layered architecture,
  contract-first API boundaries, TDD, documentation, and Pokemon data fidelity.
- `desktop_app/`: Electron desktop interface.
- `mcp_server/src/`: Python code for MCP, fetchers, ranking rules, and team-building rules.
- `mcp_server/tests/`: unit tests for MCP tools and rules.
- `docs/`: architecture and team-building documentation.
- `pokeapi/`: PokeAPI subproject used as the compatible local API.
- `docker-compose.yml`: main project compose file.
- `docker/pokeapi-compose.override.yml`: adjustments for including PokeAPI in the root compose.
- `docker/pokeapi/setup.sh`: migrates and populates PokeAPI data.
- `docker/codex/config.toml`: initial Codex configuration inside the container.

## Requirements

- Git with access to the `pokeapi` submodule.
- Docker Engine.
- Docker Compose V2, run as `docker compose`.
- `curl`, to validate the local PokeAPI after loading data.

Avoid Docker Compose V1 (`docker-compose`), which can fail with `KeyError: ContainerConfig`. The project does not need Node.js or npm installed on the host when running through Docker; the `codex` container installs the required Codex CLI.

On Debian/Ubuntu, install host tools with:

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates docker.io docker-compose-plugin
```

If the current user cannot access Docker yet, add the user to the `docker` group and open a new terminal session:

```bash
sudo usermod -aG docker "$USER"
```

Validate that Compose V2 is installed:

```bash
docker compose version
```

Optionally install the OpenSpec CLI on the host only if you will work on specification flows outside the container:

```bash
sudo apt-get install -y npm
npm install -g @fission-ai/openspec@latest
```

## Clone The Project

Clone the repository with submodules:

```bash
git clone --recurse-submodules https://github.com/JoaoFlaCruz/pokemon_party_gen.git
cd pokemon_party_gen
```

If the repository was cloned without submodules, initialize them afterward:

```bash
git submodule update --init --recursive
```

The main submodule is:

```text
pokeapi -> git@github.com:PokeAPI/pokeapi.git
```

The submodule must be present because the root compose includes `pokeapi/docker-compose.yml`, and `pokeapi-setup` uses the subproject data to populate the local database. Check that PokeAPI files exist before starting the environment:

```bash
test -f pokeapi/manage.py
test -d pokeapi/data/v2/csv
```

If you do not have an SSH key configured for GitHub, switch the submodule URL to HTTPS before initializing:

```bash
git config submodule.pokeapi.url https://github.com/PokeAPI/pokeapi.git
git submodule update --init --recursive
```

## Start From Scratch

Use these commands when you want to clean containers, volumes, and old data:

```bash
docker compose down --remove-orphans --volumes
docker compose build app codex
docker compose up -d db cache
docker compose run --rm pokeapi-setup
docker compose up -d app web graphql-engine
docker compose run --rm codex
```

`pokeapi-setup` runs:

- PokeAPI migrations;
- CSV loading through `build_all()`;
- a simple validation to avoid skipping a partial load without `PokemonCries`.

## Start Normally

After data has already been loaded once:

```bash
docker compose up -d db cache app web graphql-engine
docker compose run --rm codex
```

You can also start everything together:

```bash
docker compose up -d
docker compose run --rm codex
```

In this mode, the `codex` service opens Codex CLI in the terminal. On first use, follow the link/token login flow. The `codex_home` volume preserves login and workspace trust between runs.

## Validate The Local PokeAPI

After loading data, validate that the API returns real data:

```bash
curl -i http://127.0.0.1:8000/api/v2/
curl -i http://127.0.0.1:8000/api/v2/pokemon/charizard/
```

Default ports:

- PokeAPI REST: `http://127.0.0.1:8000/api/v2/`
- Hasura: `http://127.0.0.1:8081/`

Useful variables:

- `POKEAPI_HTTP_PORT`: host port for PokeAPI. Default: `8000`.
- `HASURA_HTTP_PORT`: host port for Hasura. Default: `8081`.
- `POKEAPI_TIMEOUT`: MCP call timeout.
- `POKEAPI_MAX_WORKERS`: MCP fetcher parallelism.

## Codex And MCP

The `codex` container uses `network_mode: host` to allow the Codex login callback on `localhost`. For that reason, MCP accesses PokeAPI through the published host port:

```text
POKEAPI_BASE_URL=http://127.0.0.1:8000/api/v2/
```

The configured MCP server is:

```text
python3 -m mcp_server.src.mcp.server
```

`docker/codex/config.toml` is copied to `CODEX_HOME/config.toml` every time the `codex` container starts. The service starts the CLI with `--dangerously-bypass-approvals-and-sandbox`; inside this container, Codex also loads `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, and the `pokemon_tools` MCP tools use `default_tools_approval_mode = "approve"`. This approval bypass applies only to the isolated Docker environment and does not change the host Codex configuration outside the `codex_home` volume.

Exposed tools include:

- `build_pokemon_team`
- `rank_pokemon`
- `rank_pokemon_moveset`
- `list_items`
- `get_type_relations`
- `ban_pokemon`

## Tests

Behavior changes follow TDD: write or update the failing automated test first,
implement the smallest passing change, then refactor. Manual checks against a
running PokeAPI supplement automated tests but do not replace them.

To run MCP unit tests:

```bash
python3 -m unittest mcp_server.tests.application.use_cases.test_build_team mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers
```

Manual tests in `mcp_server/tests/manual/` depend on an active and populated local PokeAPI.

## Desktop Interface (Electron Application)

A visual desktop application is available to manage team building interactively.

### 1. Start the HTTP API Bridge
The Electron app communicates with the Python use cases via a local HTTP server. Run the server using:

```bash
python -m mcp_server.src.application.api_server
```

This runs the server on `http://127.0.0.1:8002`.

### 2. Start the Electron Application
Navigate to the `desktop_app` directory, install dependencies, and start the app:

```bash
cd desktop_app
npm install
npm start
```

## Important Rule

Do not invent Pokemon data, and do not use external sources when the local PokeAPI should answer. If the AI says it queried an external source, first verify the local PokeAPI, data load, and `pokemon_tools` MCP server.

