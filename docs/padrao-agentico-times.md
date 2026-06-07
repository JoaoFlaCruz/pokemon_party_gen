# Padrao Agentico Para Montagem de Times

Este documento define como uma AI deve montar um time de 6 Pokemon quando o usuario fornece N Pokemon desejados. O objetivo e preservar as escolhas do usuario, completar o time de forma coerente e explicar a composicao em uma estrutura consistente.

Quando a montagem for executada por um fluxo multiagente, use tambem
`docs/fluxo-agentico-times.md`, que define os agentes A-E, suas responsabilidades
e o ciclo de validacao/refino.

## Objetivo

A AI deve receber uma lista inicial de Pokemon escolhidos pelo usuario e retornar um time completo com exatamente 6 Pokemon.

```text
entrada: N Pokemon desejados pelo usuario, onde 0 <= N <= 6
saida: 6 Pokemon estruturados, sendo N fixos do usuario e 6 - N escolhidos pela AI
```

## Regras Gerais

- O time final deve ter exatamente 6 Pokemon.
- O time deve ser estruturado em dois trios de 3 Pokemon.
- Cada trio deve ter um ace proprio e uma estrategia distinta.
- Os dois trios devem ser complementares no time completo, mas distintos o
  bastante para oferecer rotas competitivas diferentes.
- Quando o usuario informar apenas um ace ou uma estrategia, a AI deve preservar
  esse ace como fixo e selecionar um segundo ace com estrategia diferente para o
  trio complementar.
- Pokemon escolhidos pelo usuario sao prioridade e devem ser preservados na ordem informada.
- Se o usuario informar mais de 6 Pokemon, use apenas os 6 primeiros e avise que o limite foi aplicado.
- Se o usuario repetir um Pokemon, mantenha apenas a primeira ocorrencia e complete as vagas restantes.
- Nao invente Pokemon, tipos, habilidades, golpes, stats ou itens.
- Quando precisar de dados, use as tools disponiveis do projeto ou uma fonte compativel com PokeAPI.
- Quando houver incerteza de dados ou regras de jogo, declare a incerteza em vez de preencher com suposicoes.

## Papel dos Pokemon Informados Pelo Usuario

Os Pokemon informados pelo usuario devem ser tratados como escolhas fixas, nao como sugestoes descartaveis.

Para cada Pokemon escolhido pelo usuario, a AI deve estruturar:

- `name`: nome canonico ou identificador consultavel.
- `source`: `user`.
- `locked`: `true`.
- `reason`: motivo pelo qual foi mantido, normalmente "Escolha informada pelo usuario".
- `role`: papel no time, quando puder ser inferido.
- `notes`: observacoes importantes, como cobertura, redundancia ou lacunas.

Se algum Pokemon informado nao puder ser encontrado ou validado, a AI deve:

- manter o nome informado em uma secao de pendencias;
- nao inventar dados para ele;
- pedir confirmacao ou sugerir consultar novamente com outro identificador.

## Selecao Dos Pokemon Pela AI

As vagas restantes devem ser preenchidas pela AI ate completar 6 membros.

Cada Pokemon selecionado pela AI deve ter:

- `source`: `ai`.
- `locked`: `false`.
- `reason`: motivo objetivo da escolha.
- `role`: papel pretendido no time.
- `replaces_gap`: lacuna que ele ajuda a cobrir.

A selecao pode ser chamada de aleatoria apenas quando houver uma etapa real de escolha entre candidatos validos. Mesmo assim, a aleatoriedade deve ser controlada por criterios.

Ordem recomendada:

1. Identificar os tipos e papeis dos Pokemon fixos do usuario.
2. Definir o primeiro ace e sua estrategia principal.
3. Selecionar ou confirmar um segundo ace com estrategia diferente.
4. Montar dois trios de 3 Pokemon, cada um com um ace e dois suportes.
5. Levantar lacunas de cada trio e do time completo.
6. Criar um conjunto de candidatos validos para cada lacuna.
7. Escolher candidatos que preservem a identidade de cada trio e reduzam mais lacunas no conjunto.
8. Quando houver empate entre candidatos equivalentes, selecionar aleatoriamente ou declarar o criterio de desempate.

## Estrutura Dos Trios

O time deve conter:

- `trio_principal`: inclui o ace informado pelo usuario quando houver, sua
  estrategia principal e dois Pokemon que habilitam, protegem ou ampliam esse
  plano.
- `trio_complementar`: inclui um segundo ace, uma estrategia diferente da
  principal e dois Pokemon que sustentam esse segundo plano.

As estrategias dos dois trios nao devem ser apenas variacoes cosmeticas do mesmo
plano. Exemplos de diferenca real incluem clima vs setup, bulky balance vs
speed control, wallbreak especial vs limpeza fisica, hazards vs pivot ofensivo,
ou stall/burn control vs hyper offense.

Os trios precisam se complementar no time completo. Um trio pode cobrir
fraquezas defensivas do outro, fornecer controle de hazards, abrir caminho para
o outro ace, oferecer uma rota de fim de jogo diferente ou absorver matchups
ruins para a estrategia principal.

## Criterios de Composicao

A AI deve buscar equilibrio pratico, nao perfeicao competitiva absoluta.

Prioridades:

- Dois aces com estrategias diferentes e papeis claramente explicados.
- Dois trios identificaveis, cada um com plano proprio.
- Complementaridade entre os trios sem fundir ambos em uma unica estrategia.
- Cobertura de tipos ofensiva e defensiva.
- Evitar excesso de fraquezas compartilhadas.
- Incluir mistura de atacantes fisicos e especiais.
- Incluir pelo menos um Pokemon mais resistente quando possivel.
- Evitar seis Pokemon com o mesmo papel.
- Considerar utilidade de golpes de status ou suporte quando os dados estiverem disponiveis.
- Considerar itens seguraveis quando a pergunta envolver itemizacao.

Quando as tools do projeto estiverem disponiveis:

- Use `rank_pokemon` para buscar bons candidatos por tipo ou perfil de stats.
- Use `rank_pokemon_moveset` para avaliar golpes de um Pokemon candidato.
- Use `list_items` para consultar itens gerais, categorias e descricoes.

## Papeis Sugeridos

Use estes papeis como vocabulario padrao:

- `physical-attacker`: atacante fisico.
- `special-attacker`: atacante especial.
- `mixed-attacker`: atacante misto.
- `physical-wall`: resistente fisico.
- `special-wall`: resistente especial.
- `support`: suporte, controle ou status.
- `speed-control`: foco em velocidade, prioridade ou controle de ritmo.
- `type-coverage`: escolha feita principalmente para cobertura de tipos.
- `flex`: papel flexivel quando nao houver dados suficientes.

## Estrutura de Resposta

A AI deve responder com esta estrutura:

```text
Time final
Trio principal - estrategia=...
1. Pokemon - source=user|ai - role=ace|...
   Motivo: ...
   Observacoes: ...

Trio complementar - estrategia=...
4. Pokemon - source=user|ai - role=ace|...
   Motivo: ...
   Observacoes: ...

Analise do time
- Pontos fortes: ...
- Diferenca entre os trios: ...
- Como os trios se complementam: ...
- Lacunas ou riscos: ...
- Criterio usado para completar: ...

Pendencias
- Dados nao encontrados, incertezas ou confirmacoes necessarias.
```

Quando a resposta precisar ser consumida por outro agente ou sistema, use estrutura JSON:

```json
{
  "team_size": 6,
  "user_requested": ["pokemon-a"],
  "team_structure": {
    "primary_trio_strategy": "estrategia-a",
    "complementary_trio_strategy": "estrategia-b"
  },
  "team": [
    {
      "name": "pokemon-a",
      "source": "user",
      "locked": true,
      "role": "ace",
      "trio": "primary",
      "reason": "Escolha informada pelo usuario.",
      "notes": []
    },
    {
      "name": "pokemon-b",
      "source": "ai",
      "locked": false,
      "role": "type-coverage",
      "trio": "complementary",
      "reason": "Cobre uma lacuna de tipo do time.",
      "replaces_gap": "cobertura defensiva",
      "notes": []
    }
  ],
  "analysis": {
    "strengths": [],
    "trio_differences": [],
    "trio_complementarity": [],
    "risks": [],
    "selection_criteria": []
  },
  "pending": []
}
```

## Regras de Explicacao

- Explique por que cada Pokemon da AI foi escolhido.
- Explique quem sao os dois aces e qual estrategia cada um lidera.
- Explique como os dois trios sao distintos e como se complementam.
- Diferencie claramente escolhas do usuario de escolhas da AI.
- Nao apresente Pokemon selecionado pela AI como se fosse escolha do usuario.
- Se a selecao for aleatoria entre candidatos equivalentes, diga quais criterios criaram o grupo de candidatos.
- Evite respostas que apenas listem nomes; sempre inclua funcao e justificativa.

## Exemplo

Entrada do usuario:

```text
Quero montar um time com pikachu e charizard.
```

Resposta esperada:

```text
Time final
Trio principal - estrategia=cobertura eletrica e pressao de velocidade
1. pikachu - source=user - role=ace
   Motivo: Escolha informada pelo usuario.
   Observacoes: Pode atuar como atacante eletrico rapido.

2. pokemon-b - source=ai - role=speed-control
   Motivo: Apoia a estrategia do primeiro ace.
   Observacoes: Ajuda a manter ritmo ofensivo.

3. pokemon-c - source=ai - role=physical-wall
   Motivo: Completa uma lacuna defensiva do trio principal.
   Observacoes: Escolhido entre candidatos resistentes.

Trio complementar - estrategia=wallbreak especial com suporte defensivo
4. charizard - source=user - role=ace
   Motivo: Escolha informada pelo usuario.
   Observacoes: Lidera a segunda rota ofensiva do time.

5. pokemon-d - source=ai - role=support
   Motivo: Sustenta a estrategia do segundo ace.
   Observacoes: Ajuda a proteger o trio complementar.

6. pokemon-e - source=ai - role=type-coverage
   Motivo: Cobre fraquezas compartilhadas entre os trios.
   Observacoes: Tambem cria entrada segura para o trio principal.

Analise do time
- Pontos fortes: cobertura eletrica e fogo ja iniciada pelos Pokemon do usuario.
- Diferenca entre os trios: o primeiro trio joga por velocidade; o segundo por wallbreak especial.
- Como os trios se complementam: um trio pressiona checks rapidos enquanto o outro quebra defensores resistentes.
- Lacunas ou riscos: verificar fraquezas compartilhadas antes de confirmar os quatro membros restantes.
- Criterio usado para completar: preservar escolhas fixas, reduzir fraquezas repetidas e balancear papeis.

Pendencias
- Validar dados finais com as tools antes de fechar movesets e itens.
```
