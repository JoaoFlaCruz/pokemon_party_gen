# CODEX

Este arquivo define as regras de construcao e manutencao deste projeto para agentes Codex.

## Objetivo do Projeto

O projeto e um conjunto de utilitarios Python para consultar uma API compativel com PokeAPI, calcular rankings de Pokemon e golpes, e expor a funcionalidade de ranking de moveset como ferramenta MCP.

## Arquitetura Esperada

Preserve a separacao de responsabilidades:

- `src/config.py`: configuracao e leitura de `.env`.
- `src/fetch/`: acesso HTTP e adaptacao de respostas da PokeAPI.
- `src/script/`: regras de negocio, ranking e CLIs.
- `src/tool/`: wrappers para ferramentas de IA e servidor MCP. Cada tool deve ter schema, executor e apresentacao textual quando aplicavel.
- `src/test_scripts.py`: testes unitarios das regras.
- `src/test_tools.py`: testes unitarios das ferramentas e MCP.
- `src/test_fetch_calls.py`: chamadas manuais contra API local.

Novas implementacoes devem seguir a camada mais apropriada. Nao misture regra de ranking com HTTP nem coloque logica de API dentro de wrappers MCP.

## Funcionalidades Atuais

- Buscar Pokemon por tipo, habilidade e golpe aprendido.
- Buscar todos os golpes aprendidos por um Pokemon e enriquecer cada golpe com detalhes.
- Buscar itens que um Pokemon pode segurar e enriquecer cada item com suas caracteristicas.
- Buscar relacoes de efetividade, resistencia e imunidade entre tipos Pokemon.
- Ranquear Pokemon por stats defensivos mais um atributo ofensivo selecionado, excluindo lendarios e formas marcadas como `is_battle_only=true`.
- Ranquear moveset de um Pokemon conforme melhor atributo ofensivo.
- Expor `get_type_relations` via wrapper de tool e servidor MCP stdio.
- Expor `list_pokemon_held_items` via wrapper de tool e servidor MCP stdio.
- Expor `rank_pokemon` via wrapper de tool e servidor MCP stdio.
- Expor `rank_pokemon_moveset` via wrapper de tool e servidor MCP stdio.

## Regras Agenticas

- Para pedidos de montagem de time de 6 Pokemon a partir de N Pokemon desejados pelo usuario, siga `docs/padrao-agentico-times.md`.
- Preserve as escolhas do usuario como membros fixos do time e diferencie claramente Pokemon escolhidos pelo usuario de Pokemon selecionados pela AI.
- Ao completar vagas restantes, use criterios explicitos de cobertura, papeis e lacunas; nao invente dados de Pokemon.

## Regras de Implementacao

- Use Python padrao e mantenha o estilo simples ja existente.
- Prefira funcoes puras para regras de ranking.
- Injete fetchers ou use protocolos/fakes nos testes quando a regra nao precisar de HTTP real.
- Use `ThreadPoolExecutor` apenas na camada de busca quando houver chamadas independentes.
- Ao criar fetchers novos, exporte-os em `src/fetch/__init__.py` e mantenha a saida JSON-serializavel.
- Preserve respostas estruturadas com dicionarios JSON-serializaveis.
- Valide argumentos publicos em wrappers e CLIs.
- Ao criar uma nova tool, registre-a no MCP para `tools/list` e `tools/call`.
- Nao invente dados de Pokemon; consulte uma fonte compativel com PokeAPI quando dados reais forem necessarios.
- No ranking de Pokemon, exclua especies com `is_legendary=true` e formas com `is_battle_only=true`, pois essas formas nao sao elencaveis como membros resolvidos para PvP.

## Documentacao Obrigatoria

Qualquer nova implementacao ou alteracao de comportamento deve atualizar a documentacao do projeto.

Atualize `docs/arquitetura.md` quando mudar qualquer um destes pontos:

- estrutura de pastas ou modulos;
- contratos de entrada ou saida;
- regras de ranking;
- variaveis de ambiente;
- comandos de execucao ou teste;
- ferramentas MCP ou schemas;
- dependencias externas;
- fluxo de dados entre camadas.

Atualize `docs/padrao-agentico-times.md` quando mudar regras de montagem de times, formato de resposta para times, papeis sugeridos ou criterio de selecao de Pokemon pela AI.

Se uma mudanca for pequena e nao alterar comportamento ou arquitetura, registre explicitamente no resumo final que a documentacao foi revisada e nao exigiu alteracao.

## Testes

Antes de finalizar alteracoes de codigo, rode quando possivel:

```bash
python3 -m unittest src.test_scripts src.test_tools src.test_fetchers
```

Para fetchers, `src/test_fetch_calls.py` depende de uma PokeAPI local ativa e populada. Nao trate esse arquivo como teste unitario automatico.

## Checklist Para Mudancas

- A mudanca ficou na camada correta?
- O contrato de resposta continua JSON-serializavel?
- As regras novas ou alteradas possuem teste unitario?
- A documentacao em `docs/arquitetura.md` foi atualizada quando necessario?
- O comportamento MCP continua compativel com `tools/list` e `tools/call`?
