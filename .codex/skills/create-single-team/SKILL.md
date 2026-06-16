---
name: create-single-team
description: Use when Codex needs to create a list of N Pokemon single battle teams with 6 Pokemon each, centered on one or two ace Pokemon, distinct trio strategies, and team count. Trigger for requests to build multiple varied single battle teams, compare team variants, or generate cohesive Pokemon team options around aces.
---

# Create Single Team

## Objetivo

Criar uma lista de `n` times para single battle, cada um com exatamente 6 Pokemon, mantendo dois trios de 3 Pokemon com aces e estrategias distintas, coesao estrategica, protecao de tipagem, habilidades compativeis e variacao suficiente para analise entre alternativas.

## Caminhos do Projeto

As tools MCP e regras usadas por este fluxo vivem em `mcp_server/src/`. Os testes automatizados correspondentes vivem em `mcp_server/tests/`. Ao orientar manutencao ou validar comandos, use os caminhos encapsulados, por exemplo `mcp_server/src/mcp/tools/` para tools e `mcp_server/tests/mcp/tools/` para testes de tools.

## Entrada Obrigatoria

Antes de montar os times, pedir ao usuario:

1. Pokemon ace principal.
2. Estrategia base do ace principal.
3. Numero de times desejados.
4. Segundo ace ou segunda estrategia, quando o usuario quiser fixa-los.

Se algum desses dados ja estiver claro na conversa, reutilizar o dado informado e pedir apenas o que faltar.

## Fluxo Agentico

Seguir o fluxo definido em `docs/agentic-team-flow.md` e o padrao de resposta
em `docs/agentic-team-pattern.md`. `build_pokemon_team` nao e uma tool MCP
ativa e nao deve ser usado para construcao de times; a montagem e
responsabilidade do fluxo agentico com tools de dados de nivel inferior.

1. Definir o pedido inicial: confirmar ace principal, estrategia base e quantidade de times.
2. Agente A: coletar dados dos Pokemon informados, golpes, itens e relacoes de tipo quando necessarias.
   - Para pedidos Pokemon Champions only, usar `validate_champions_legality` quando houver duvida sobre legalidade, completude de dados, golpes, habilidades ou itens.
   - Para pedidos de clima ou mecanica especifica, construir os papeis dentro do fluxo A-F, como rain setter, rain attacker, pivots defensivos, checks de cobertura, speed control e win condition. Nao chamar `search_champions_strategy`; a selecao estrategica e responsabilidade dos agentes. Usar `rank_pokemon`, `rank_pokemon_moveset`, `validate_champions_legality`, `get_type_relations` e `list_items` para provar criterios de ability, golpe, tipo, stat profile, item e matchup sem inventar fatos.
3. Agente B: montar o trio principal com o ace informado, estrategia, movesets, habilidades, distribuicao de stats e itens, preservando as escolhas do usuario.
4. Agente E: selecionar ou confirmar um segundo ace com estrategia distinta para o trio complementar.
5. Agente E: listar candidatos para completar os dois trios e reduzir fraquezas antes da validacao final.
6. Agente A: validar os dados dos candidatos escolhidos.
7. Agente B: integrar os candidatos e separar trio principal e trio complementar.
8. Agente C: validar regras de equipe, repeticoes de Pokemon, repeticoes de item quando aplicavel, dois aces e coesao entre Pokemon.
9. Agente D: auditar tipos, velocidades, stats de ataque e defesa, papeis, diferenca entre trios e fraquezas do time.
10. Quando C ou D apontarem lacuna relevante, retornar ao Agente E para selecionar substitutos ou ajustes e repetir o ciclo ate o time ficar valido ou a pendencia precisar de confirmacao do usuario.
11. Agente F: popular os detalhes finais de cada Pokemon de acordo com role, trio, estrategia e dados validados: quatro golpes com motivo, EVs com pontos, natureza, item e sugestao de uso.
12. Agente F deve executar uma validacao de completude para cada Pokemon final. Um Pokemon final so esta completo quando tiver nome, source, locked, role, trio, motivo, quatro golpes com motivo, EVs com stats e pontos, natureza, item, sugestao, notes e, para escolhas da IA, a lacuna coberta.
13. Se faltar um dado obrigatorio e uma tool de dados puder resolver a lacuna com uma chamada focada, retornar ao Agente A para coletar esse dado e entao atualizar os detalhes com o Agente F.
14. Se uma troca de Pokemon, role, estrategia de trio ou lacuna prioritaria acontecer apos refinamento, o Agente F deve revisar os Pokemon afetados antes da resposta final.

Cada time final deve unir:

- trio principal com o ace principal;
- trio complementar com um segundo ace;
- estrategias diferentes entre os dois trios;
- complementaridade defensiva, ofensiva ou utilitaria entre os trios;
- exatamente 6 Pokemon;
- detalhes finais completos populados pelo Agente F;
- nenhuma entrada final aceita com campo obrigatorio ausente;
- pendencias declaradas quando golpes, EVs, natureza, item ou outro campo obrigatorio nao puderem ser validados ou justificados.

## Estrutura Dos Trios

O trio principal deve conter o ace principal e dois Pokemon compativeis com a estrategia,
cobrindo lacunas de tipagem, funcoes e habilidades. O trio complementar deve
conter um segundo ace e dois Pokemon adicionais, com uma estrategia diferente da
principal e uma rota competitiva propria.

O segundo ace nao deve ser apenas um suporte do ace principal. Ele deve liderar
um plano alternativo real, como setup, speed control, hazards, bulky balance,
wallbreak fisico/especial, controle de status ou outra rota coerente.

Os dois trios devem se complementar no time completo: um pode abrir caminho para
o outro, cobrir fraquezas de tipo, controlar hazards, absorver matchups ruins ou
oferecer uma condicao de vitoria diferente.

## Criterios de Selecao

Priorizar:

- dois aces com estrategias diferentes;
- coesao com a estrategia base;
- compatibilidade com o ace principal e com o segundo ace;
- protecao de tipagem dos dois aces, dos dois trios e do time inteiro;
- habilidades que apoiem a estrategia ou reduzam riscos;
- movesets, distribuicao de stats e itens coerentes com os papeis escolhidos;
- Pokemon versateis, capazes de cumprir mais de uma funcao;
- equilibrio entre pressao ofensiva, resistencia, suporte e controle de ritmo;
- variedade real entre times para comparacao;
- diferenca clara entre trio principal e trio complementar.

Nao inventar Pokemon, tipos, habilidades, golpes, stats, EVs, naturezas ou itens. Quando dados reais forem necessarios, usar as tools do projeto ou uma fonte compativel com PokeAPI. Se a ferramenta disponivel nao retornar um dado exigido, declarar a pendencia em vez de preencher por suposicao. Nao apresentar um time como final aceito quando qualquer Pokemon estiver incompleto; nesse caso, parar com `Pendencias` ou pedir confirmacao do usuario.

Para chuva, sol, clima, terrain ou outra estrategia baseada em mecanica, nao inferir setters, abusers, legalidade, golpes, habilidades ou itens por conhecimento externo. Validar os Pokemon fixos e entidades propostas com `validate_champions_legality`, buscar candidatos com tools factuais de nivel inferior, e carregar diagnosticos estruturados como `pokemon_not_found`, `outside_champions_scope`, `incomplete_data`, `source_unavailable`, `unsupported_validation` ou `no_eligible_candidates` para `Pendencias` quando bloquearem o time final. O agente deve formular internamente o caso estrategico mais rico possivel, mas executar a verificacao por dados: filtros de `rank_pokemon`, checks focados de legalidade, movesets, itens e relacoes de tipo. Se uma informacao nao puder ser validada ou justificada, omitir essa regra e registrar a lacuna em `Pendencias`.

## Variacao Entre Times

Ao gerar varios times:

- cada time pode compartilhar no maximo 4 Pokemon com outro time;
- pelo menos 2 Pokemon devem variar entre quaisquer dois times comparados;
- manter o ace quando ele for parte obrigatoria do pedido;
- variar segundos aces, estrategias complementares, complementos, papeis secundarios ou cobertura quando possivel;
- evitar produzir times quase identicos com pequenas mudancas cosmeticas.

Se a quantidade de times pedida tornar dificil manter variacao real, declarar a limitacao e explicar o criterio usado.

## Formato de Resposta

Responder em portugues, com esta estrutura:

```text
Premissas
- Ace principal: ...
- Estrategia principal: ...
- Segundo ace: ...
- Estrategia complementar: ...
- Numero de times: ...

Time 1
Trio principal - estrategia=...
1. pokemon - source=user|ai - locked=true|false - role=ace|...
   Motivo: ...
   Lacuna coberta: ... (apenas source=ai)
   Golpes:
   - golpe A: motivo
   - golpe B: motivo
   - golpe C: motivo
   - golpe D: motivo
   EVs: stat A XXX pts + stat B XXX pts + stat C XXX pts
   Natureza: ...
   Item: ...
   Sugestao: ...
   Notes: ...
2. pokemon - source=user|ai - locked=true|false - role=...
   Motivo: ...
   Lacuna coberta: ... (apenas source=ai)
   Golpes:
   - golpe A: motivo
   - golpe B: motivo
   - golpe C: motivo
   - golpe D: motivo
   EVs: stat A XXX pts + stat B XXX pts + stat C XXX pts
   Natureza: ...
   Item: ...
   Sugestao: ...
   Notes: ...
3. pokemon - source=user|ai - locked=true|false - role=...
   Motivo: ...
   Lacuna coberta: ... (apenas source=ai)
   Golpes:
   - golpe A: motivo
   - golpe B: motivo
   - golpe C: motivo
   - golpe D: motivo
   EVs: stat A XXX pts + stat B XXX pts + stat C XXX pts
   Natureza: ...
   Item: ...
   Sugestao: ...
   Notes: ...

Trio complementar - estrategia=...
4. pokemon - source=user|ai - locked=true|false - role=ace
   Motivo: ...
   Lacuna coberta: ... (apenas source=ai)
   Golpes:
   - golpe A: motivo
   - golpe B: motivo
   - golpe C: motivo
   - golpe D: motivo
   EVs: stat A XXX pts + stat B XXX pts + stat C XXX pts
   Natureza: ...
   Item: ...
   Sugestao: ...
   Notes: ...
5. pokemon - source=user|ai - locked=true|false - role=...
   Motivo: ...
   Lacuna coberta: ... (apenas source=ai)
   Golpes:
   - golpe A: motivo
   - golpe B: motivo
   - golpe C: motivo
   - golpe D: motivo
   EVs: stat A XXX pts + stat B XXX pts + stat C XXX pts
   Natureza: ...
   Item: ...
   Sugestao: ...
   Notes: ...
6. pokemon - source=user|ai - locked=true|false - role=...
   Motivo: ...
   Lacuna coberta: ... (apenas source=ai)
   Golpes:
   - golpe A: motivo
   - golpe B: motivo
   - golpe C: motivo
   - golpe D: motivo
   EVs: stat A XXX pts + stat B XXX pts + stat C XXX pts
   Natureza: ...
   Item: ...
   Sugestao: ...
   Notes: ...

Analise do time
- Plano principal: ...
- Plano complementar: ...
- Diferenca entre os trios: ...
- Como os trios se complementam: ...
- Cobertura e protecoes: ...
- Riscos: ...

Comparacao entre times
- Variacoes relevantes: ...
- Pokemon compartilhados: ...
- Pokemon que mudam: ...

Pendencias
- Dados nao validados, incertezas ou confirmacoes necessarias.
```

Quando o usuario pedir JSON, preservar as mesmas informacoes em campos estruturados.
