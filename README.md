# Pokemon Party Gen

Projeto com utilitarios Python para consultar uma PokeAPI local, ranquear Pokemon
e golpes, e expor essas funcoes como ferramentas MCP para uso pelo Codex.

O ambiente Docker da raiz sobe:

- PokeAPI local, usando o compose interno em `pokeapi/`;
- Postgres, Redis, Nginx e Hasura da PokeAPI;
- um terminal interativo com Codex CLI;
- o MCP `pokemon_tools`, apontando para `mcp_server/src/mcp/server.py`.

## Estrutura Basica

- `mcp_server/src/`: codigo Python do MCP, fetchers e regras de ranking.
- `mcp_server/tests/`: testes unitarios do MCP e regras.
- `docs/`: arquitetura e regras de montagem de times.
- `pokeapi/`: subprojeto PokeAPI usado como API local compativel.
- `docker-compose.yml`: compose principal do projeto.
- `docker/pokeapi-compose.override.yml`: ajustes para incluir a PokeAPI no compose da raiz.
- `docker/pokeapi/setup.sh`: migra e popula dados da PokeAPI.
- `docker/codex/config.toml`: configuracao inicial do Codex no container.

## Requisitos

- Docker com Docker Compose V2.
- Use `docker compose`, com espaco.
- Evite `docker-compose` V1, pois ele pode falhar com `KeyError: ContainerConfig`.

## Subir do Zero

Use estes comandos quando quiser limpar containers, volumes e dados antigos:

```bash
docker compose down --remove-orphans --volumes
docker compose build app codex
docker compose up -d db cache
docker compose run --rm pokeapi-setup
docker compose up -d app web graphql-engine
docker compose run --rm codex
```

O `pokeapi-setup` executa:

- migrations da PokeAPI;
- carga dos CSVs via `build_all()`;
- validacao simples para evitar pular uma carga parcial sem `PokemonCries`.

## Subir Normalmente

Depois que os dados ja foram carregados uma vez:

```bash
docker compose up -d db cache app web graphql-engine
docker compose run --rm codex
```

Tambem e possivel subir tudo junto:

```bash
docker compose up
```

Nesse modo, o servico `codex` abre o Codex CLI no terminal. No primeiro uso, siga o fluxo de login
por link/token. O volume `codex_home` preserva login e confianca do workspace entre execucoes.

## Validar a PokeAPI Local

Depois da carga, valide que a API responde com dados reais:

```bash
curl -i http://127.0.0.1:8000/api/v2/
curl -i http://127.0.0.1:8000/api/v2/pokemon/charizard/
```

Portas padrao:

- PokeAPI REST: `http://127.0.0.1:8000/api/v2/`
- Hasura: `http://127.0.0.1:8081/`

Variaveis uteis:

- `POKEAPI_HTTP_PORT`: porta host da PokeAPI. Padrao: `8000`.
- `HASURA_HTTP_PORT`: porta host do Hasura. Padrao: `8081`.
- `POKEAPI_TIMEOUT`: timeout das chamadas do MCP.
- `POKEAPI_MAX_WORKERS`: paralelismo dos fetchers do MCP.

## Codex e MCP

O container `codex` usa `network_mode: host` para permitir o callback de login do Codex em
`localhost`. Por isso, o MCP acessa a PokeAPI pela porta publicada no host:

```text
POKEAPI_BASE_URL=http://127.0.0.1:8000/api/v2/
```

O servidor MCP configurado e:

```text
python3 -m mcp_server.src.mcp.server
```

As ferramentas expostas incluem:

- `rank_pokemon`
- `rank_pokemon_moveset`
- `list_items`
- `get_type_relations`
- `ban_pokemon`

## Testes

Para rodar os testes unitarios do MCP:

```bash
python3 -m unittest mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers
```

Os testes manuais em `mcp_server/tests/manual/` dependem da PokeAPI local ativa e populada.

## Regra Importante

Nao invente dados de Pokemon e nao use fontes externas quando a PokeAPI local deve responder.
Se a IA disser que consultou fonte externa, primeiro verifique a PokeAPI local, a carga de dados
e o MCP `pokemon_tools`.
