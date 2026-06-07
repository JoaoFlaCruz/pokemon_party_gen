# Arquitetura do Projeto

Este projeto fornece utilitarios Python para consultar uma API compativel com a PokeAPI, ranquear Pokemon e golpes, e expor uma ferramenta MCP para uso por agentes.

## Estrutura

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
                item_tool.py
                pokemon_moveset_tool.py
                pokemon_ranking_tool.py
                type_relations_tool.py
                __init__.py
        application/
            use_cases/
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

## Configuracao

`mcp_server/src/config/env.py` carrega variaveis de ambiente a partir de um arquivo `.env` na raiz do projeto, sem sobrescrever valores ja definidos no ambiente.

Variaveis suportadas:

- `POKEAPI_BASE_URL`: URL base da API. Valor padrao: `http://localhost/api/v2/`.
- `POKEAPI_TIMEOUT`: timeout das chamadas HTTP. Valor padrao: `30.0`.
- `POKEAPI_MAX_WORKERS`: quantidade padrao de workers paralelos. Valor padrao: `12`.
- `BANNED_POKEMON_DB_PATH`: caminho do banco SQLite com Pokemon proibidos para a tool `rank_pokemon`. Valor padrao: `banned_pokemon.sqlite3` na raiz do projeto.

## Camada de Busca

`mcp_server/src/infrastructure/pokeapi/` concentra os clientes HTTP. Essa camada conhece a API externa e retorna dados estruturados para as regras de negocio.

`PokemonFetcher` busca Pokemon e seus stats. Ele tambem consulta `pokemon-species/{name}` para excluir especies lendarias do ranking e consulta `pokemon-form/{name}` para excluir formas marcadas como `is_battle_only=true`, que representam formas temporarias ou restritas a batalha e nao devem ser elencadas como membros resolvidos para PvP. Para Pokemon aceitos, o retorno inclui `is_battle_only=false` e preserva `is_mega`, `base_pokemon` e `required_item` quando esses metadados existirem e o item puder ser validado no endpoint `item/{name}`. Ele aceita filtros por:

- tipo, com ate dois tipos;
- habilidade;
- golpe aprendido.

Quando filtros sao combinados, o resultado e a intersecao dos Pokemon encontrados em cada filtro. Depois, os detalhes de cada Pokemon sao buscados em paralelo com `ThreadPoolExecutor`.

`PokemonMovesFetcher` busca um Pokemon por nome ou ID e enriquece cada golpe aprendido com detalhes do endpoint `move/{name}/`. Os detalhes de golpes tambem sao buscados em paralelo.

`ItemFetcher` lista itens gerais pelo endpoint `item/?limit={limit}&offset={offset}` e enriquece cada resultado com detalhes do endpoint `item/{name}/`. A resposta inclui paginacao (`count`, `next`, `previous`, `limit`, `offset`) e caracteristicas do item como `cost`, `fling_power`, `fling_effect`, `attributes`, `category`, `effect_entries`, `flavor_text_entries` e `sprites`.

`TypeRelationsFetcher` busca um tipo por nome ou ID no endpoint `type/{name}/` e normaliza `damage_relations` em duas perspectivas: `offensive`, com `super_effective_against`, `weak_against` e `no_effect_against`; e `defensive`, com `weak_to`, `resists` e `immune_to`. O retorno tambem preserva `raw_damage_relations`.

## Camada de Regras

`mcp_server/src/application/use_cases/` contem a logica de ranking e tambem pode ser executado por CLI.

`rank_pokemon.py` ranqueia Pokemon nao lendarios e nao marcados como `is_battle_only`, por uma pontuacao base formada por:

```text
hp + defense + special-defense + atributo ofensivo selecionado
```

O atributo ofensivo pode ser:

- `auto`: escolhe `attack` ou `special-attack`, o que for maior para cada Pokemon;
- `attack`: forca ataque fisico;
- `special-attack`: forca ataque especial.

Opcionalmente, `priority_stat` pode escolher um stat para receber multiplicador `1.4` na pontuacao. Os valores aceitos sao `hp`, `attack`, `defense`, `special-attack`, `special-defense` e `speed`. Quando o stat priorizado nao estiver na pontuacao base, ele passa a compor o calculo.

`speed_mode` controla como velocidade participa do ranking:

- `ignore`: mantem o comportamento anterior e ignora `speed`;
- `high`: adiciona `speed` ao calculo, favorecendo Pokemon rapidos;
- `low`: adiciona `255 - speed` ao calculo, favorecendo Pokemon lentos.

`rank_moveset.py` ranqueia golpes de um Pokemon. Primeiro escolhe o melhor atributo ofensivo do Pokemon:

- `attack` seleciona golpes `physical`;
- `special-attack` seleciona golpes `special`.

Golpes ofensivos da categoria selecionada sao ordenados pela regra:

```text
accuracy * 1.4 + power
```

Empates usam, nessa ordem, maior accuracy, maior power e nome do golpe. Golpes `status` nao recebem rank e sao adicionados ao fim do resultado.

## Camada de Ferramenta

`mcp_server/src/mcp/tools/` expoe funcionalidades do projeto para uso por agentes.

`banned_pokemon_tool.py` define a tool `ban_pokemon`, valida `id` e `name`, cria a tabela SQLite `banned_pokemon (id, name)` quando necessario e registra o Pokemon no banco de exclusao configurado por `BANNED_POKEMON_DB_PATH`. A operacao e idempotente para registros ja existentes por mesmo `id` ou mesmo `name`.

`item_tool.py` define a tool `list_items`, valida `limit` e `offset`, chama `ItemFetcher` e retorna uma listagem geral de itens com uma apresentacao textual resumida para consumo de AI. A apresentacao inclui categoria, custo, atributos e descricao do item a partir de `effect_entries` ou `flavor_text_entries`, priorizando texto em ingles quando disponivel.

`type_relations_tool.py` define a tool `get_type_relations`, valida `type`, chama `TypeRelationsFetcher` e retorna relacoes ofensivas e defensivas de tipo em formato estruturado e textual.

`pokemon_ranking_tool.py` define a tool `rank_pokemon`, valida filtros opcionais de tipo, `offense_stat`, `priority_stat`, `speed_mode` e `head_size`, chama `rank_pokemon.py` e retorna ranking estruturado com apresentacao textual. Os resultados ja chegam filtrados para remover especies lendarias e formas `is_battle_only`. Depois do ranking, a tool tambem consulta o SQLite configurado em `BANNED_POKEMON_DB_PATH` e remove da listagem qualquer Pokemon cadastrado na tabela `banned_pokemon`, com colunas `id` e `name`. Se o arquivo do banco nao existir, nenhum filtro adicional e aplicado.

`pokemon_moveset_tool.py` define a tool `rank_pokemon_moveset`, valida argumentos, chama a regra de ranking e retorna:

- `tool_name`;
- `input`;
- `data`, com o resultado estruturado;
- `presentation`, com uma resposta textual resumida.

`mcp_server/src/mcp/server.py` implementa um servidor MCP stdio minimo com suporte a:

- `initialize`;
- `ping`;
- `tools/list`;
- `tools/call`.

A chamada `tools/call` despacha pelo nome da tool e suporta `ban_pokemon`, `get_type_relations`, `list_items`, `rank_pokemon` e `rank_pokemon_moveset`, retornando conteudo textual e `structuredContent`.

## Testes

Os testes unitarios principais ficam em:

- `mcp_server/tests/application/use_cases/test_rankings.py`: testa regras de ranking com fakes, sem depender de HTTP.
- `mcp_server/tests/mcp/tools/test_tools.py`: testa schema da tool, formatacao, validacao e comportamento MCP basico.
- `mcp_server/tests/infrastructure/pokeapi/test_fetchers.py`: testa a montagem de dados de fetchers sem depender de HTTP real.

`mcp_server/tests/manual/test_fetch_calls.py` e uma verificacao manual para ser executada quando uma PokeAPI local estiver ativa e populada.

Comando recomendado para testes unitarios:

```bash
python3 -m unittest mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers
```

## Fluxo Principal

```text
CLI ou MCP/tool (`get_type_relations`, `list_items`, `rank_pokemon` ou `rank_pokemon_moveset`)
    -> mcp_server/src/application/use_cases/ ou mcp_server/src/infrastructure/pokeapi/
        -> PokeAPI REST
        -> regra de ranking/adaptacao
    -> resposta estruturada e/ou apresentacao textual

CLI ou MCP/tool (`ban_pokemon`)
    -> mcp_server/src/mcp/tools/banned_pokemon_tool.py
        -> SQLite `banned_pokemon`
    -> resposta estruturada e apresentacao textual
```

## Fluxo Agentico de Times

`docs/fluxo-agentico-times.md` define cinco agentes para montagem de times:

- Agente A: coleta dados de Pokemon, golpes, itens gerais e relacoes de tipo.
- Agente B: monta a proposta jogavel com estrategia, movesets, habilidades,
  distribuicao de stats e itens quando os dados forem validados.
- Agente E: seleciona candidatos para completar vagas ou corrigir lacunas antes
  e depois das etapas de validacao.
- Agente C: valida regras de equipe, repeticoes, itens e coesao estrategica.
- Agente D: audita tipos, velocidades, stats ofensivos e defensivos, papeis,
  fraquezas e lacunas.

Esse fluxo segue `docs/fluxograma_agentico.pdf` e deve ser usado junto com
`docs/padrao-agentico-times.md` quando uma AI precisar completar um time de 6
Pokemon com base em escolhas e estrategia do usuario.

## Principios de Manutencao

- Mantenha chamadas HTTP restritas a `mcp_server/src/infrastructure/pokeapi/`.
- Ao adicionar um fetcher, exporte-o em `mcp_server/src/infrastructure/pokeapi/__init__.py` e cubra a montagem de dados com testes sem HTTP real.
- Mantenha regras de ranking em `mcp_server/src/application/use_cases/`, testaveis com fakes.
- Mantenha wrappers de agente/MCP em `mcp_server/src/mcp/tools/` e roteamento em `mcp_server/src/mcp/server.py`.
- Ao adicionar uma tool, registre seu schema, executor, apresentacao, roteamento MCP e testes.
- Ao mudar regras, contratos de resposta, argumentos, variaveis de ambiente ou fluxo de execucao, atualize esta documentacao.
