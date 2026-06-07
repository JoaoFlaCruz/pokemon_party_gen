---
name: create-single-team
description: Use when Codex needs to create a list of N Pokemon single battle teams with 6 Pokemon each, centered on one or two ace Pokemon, distinct trio strategies, and team count. Trigger for requests to build multiple varied single battle teams, compare team variants, or generate cohesive Pokemon team options around aces.
---

# Create Single Team

## Objetivo

Criar uma lista de `n` times para single battle, cada um com exatamente 6 Pokemon, mantendo dois trios de 3 Pokemon com aces e estrategias distintas, coesao estrategica, protecao de tipagem, habilidades compativeis e variacao suficiente para analise entre alternativas.

## Entrada Obrigatoria

Antes de montar os times, pedir ao usuario:

1. Pokemon ace principal.
2. Estrategia base do ace principal.
3. Numero de times desejados.
4. Segundo ace ou segunda estrategia, quando o usuario quiser fixa-los.

Se algum desses dados ja estiver claro na conversa, reutilizar o dado informado e pedir apenas o que faltar.

## Fluxo Agentico

Seguir o fluxo definido em `docs/fluxograma_agentico.pdf` e detalhado em
`docs/fluxo-agentico-times.md`:

1. Definir o pedido inicial: confirmar ace principal, estrategia base e quantidade de times.
2. Agente A: coletar dados dos Pokemon informados, golpes, itens e relacoes de tipo quando necessarias.
3. Agente B: montar o trio principal com o ace informado, estrategia, movesets, habilidades, distribuicao de stats e itens, preservando as escolhas do usuario.
4. Agente E: selecionar ou confirmar um segundo ace com estrategia distinta para o trio complementar.
5. Agente E: listar candidatos para completar os dois trios e reduzir fraquezas antes da validacao final.
6. Agente A: validar os dados dos candidatos escolhidos.
7. Agente B: integrar os candidatos e separar trio principal e trio complementar.
8. Agente C: validar regras de equipe, repeticoes de Pokemon, repeticoes de item quando aplicavel, dois aces e coesao entre Pokemon.
9. Agente D: auditar tipos, velocidades, stats de ataque e defesa, papeis, diferenca entre trios e fraquezas do time.
10. Quando C ou D apontarem lacuna relevante, retornar ao Agente E para selecionar substitutos ou ajustes e repetir o ciclo ate o time ficar valido ou a pendencia precisar de confirmacao do usuario.

Cada time final deve unir:

- trio principal com o ace principal;
- trio complementar com um segundo ace;
- estrategias diferentes entre os dois trios;
- complementaridade defensiva, ofensiva ou utilitaria entre os trios;
- exatamente 6 Pokemon;
- movesets, habilidades, distribuicao de stats e itens quando os dados forem validados ou quando a estrategia exigir esse nivel de detalhe.

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

Nao inventar Pokemon, tipos, habilidades, golpes, stats ou itens. Quando dados reais forem necessarios, usar as tools do projeto ou uma fonte compativel com PokeAPI. Se a ferramenta disponivel nao retornar um dado exigido, declarar a pendencia em vez de preencher por suposicao.

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
1. pokemon - role=ace|...
   Motivo: ...
2. pokemon - role=...
   Motivo: ...
3. pokemon - role=...
   Motivo: ...

Trio complementar - estrategia=...
4. pokemon - role=ace
   Motivo: ...
5. pokemon - role=...
   Motivo: ...
6. pokemon - role=...
   Motivo: ...

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
