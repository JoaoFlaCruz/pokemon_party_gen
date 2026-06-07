# Fluxo Agentico Para Times Pokemon

Este documento define os cinco agentes de apoio para montagem de times de 6
Pokemon e a diretriz de fluxo de trabalho baseada no processo agentico do
projeto. Ele complementa `docs/padrao-agentico-times.md`, foi alinhado ao
fluxograma em `docs/fluxograma_agentico.pdf` e deve ser usado quando uma AI
precisar transformar escolhas iniciais do usuario em um time completo, validado
e explicado.

## Entrada

A entrada minima do fluxo e:

- nomes ou identificadores dos Pokemon escolhidos pelo usuario;
- estrategia de combate desejada, quando informada;
- segundo ace ou segunda estrategia, quando informados;
- restricoes adicionais, quando existirem, como tipo, papel, item, geracao ou
  preferencia por ataque fisico ou especial.

Pokemon informados pelo usuario sao membros fixos. O fluxo pode validar,
classificar e apontar riscos desses Pokemon, mas nao deve remove-los sem
confirmacao explicita. Quando o usuario informar apenas um ace, o fluxo deve
preserva-lo como primeiro ace e selecionar um segundo ace com estrategia distinta
para liderar o trio complementar.

## Agente A: Coletor de Dados

Responsabilidade:

- buscar dados dos Pokemon informados ou candidatos;
- buscar golpes disponiveis e dados de ataques;
- buscar itens seguraveis quando a estrategia envolver itemizacao;
- buscar relacoes de tipo quando outro agente precisar avaliar cobertura ou
  fraquezas.

Tools recomendadas:

- `rank_pokemon`, para levantar candidatos por tipo ou perfil de stats;
- `rank_pokemon_moveset`, para avaliar golpes ofensivos de um Pokemon;
- `list_items`, para consultar itens gerais e descricoes;
- `get_type_relations`, para consultar relacoes ofensivas e defensivas de tipo.

Saida esperada:

- dados estruturados e rastreaveis;
- indicacao de dados ausentes ou nao encontrados;
- nenhuma invencao de stats, tipos, golpes, habilidades ou itens.

## Agente B: Montador Base

Responsabilidade:

- montar uma primeira proposta jogavel com base na estrategia;
- preservar os Pokemon do usuario como `source=user` e `locked=true`;
- definir dois trios de 3 Pokemon, cada um com um ace e uma estrategia propria;
- selecionar ou confirmar um segundo ace quando o usuario informar apenas um;
- preencher papeis provaveis para cada membro;
- propor moveset, habilidade, distribuicao de stats e item quando os dados
  tiverem sido validados;
- explicitar lacunas que ainda precisam de candidatos do Agente E.

Diretriz:

- se o time tiver menos de 6 Pokemon, trabalhar com vagas abertas;
- se o usuario informar mais de 6 Pokemon, manter apenas os 6 primeiros e
  registrar o limite aplicado;
- evitar que a primeira proposta dependa de dados nao validados pelo Agente A.

Saida esperada:

- rascunho de time separado em trio principal e trio complementar;
- dois aces identificados com estrategias diferentes;
- papeis sugeridos;
- moveset, habilidade, distribuicao de stats e item quando disponiveis;
- lacunas iniciais conhecidas.

## Agente C: Validador Estrategico

Responsabilidade:

- validar regras gerais de montagem de time;
- verificar repeticoes de Pokemon, repeticoes de item quando a estrategia usar
  itens, membros invalidos e limite de 6 Pokemon;
- avaliar se a distribuicao de papeis e stats atende as duas estrategias declaradas ou selecionadas;
- avaliar se os dois trios possuem aces proprios, estrategias diferentes e complementaridade real;
- avaliar coesao entre Pokemon, movesets, habilidades, itens e estrategia;
- executar a etapa de reflexao antes de enviar o time para auditoria ou
  refinamento.

Criterios de validacao:

- exatamente 6 Pokemon no resultado final;
- dois trios de 3 Pokemon no resultado final;
- dois aces identificados, com estrategias distintas;
- escolhas do usuario preservadas;
- mistura razoavel de papeis quando possivel;
- justificativas objetivas para Pokemon selecionados pela AI;
- pendencias declaradas quando dados forem insuficientes.

Saida esperada:

- status `valido`, `precisa_refino` ou `bloqueado_por_dados`;
- lista de ajustes necessarios;
- recomendacao para seguir ao Agente D, retornar ao Agente B ou acionar o
  Agente E.

## Agente D: Auditor de Equilibrio

Responsabilidade:

- verificar tipos, fraquezas, resistencias e imunidades;
- identificar excesso de fraquezas compartilhadas;
- auditar cada trio separadamente e depois o time completo;
- avaliar se as fraquezas de um trio sao cobertas pelo outro;
- avaliar velocidades, stats de ataque e stats defensivos do conjunto;
- avaliar se ha redundancia excessiva de papeis;
- apontar lacunas ofensivas, defensivas e de utilidade.

Diretriz:

- usar dados do Agente A e, quando necessario, pedir novas consultas de tipo;
- declarar incertezas em vez de assumir relacoes nao consultadas;
- diferenciar risco aceitavel de bloqueio real.

Saida esperada:

- diagnostico de equilibrio do time;
- lacunas priorizadas;
- decisao `equilibrado=true|false`.

## Agente E: Seletor de Candidatos

Responsabilidade:

- listar Pokemon possiveis para completar vagas;
- selecionar segundo ace quando ele nao tiver sido informado pelo usuario;
- selecionar candidatos com base nas estrategias dos dois trios, nas lacunas e nos dados
  validados;
- operar em dois modos:
  - `selecionar_segundo_ace`: escolher um ace com estrategia diferente da
    estrategia do primeiro trio;
  - `completar_time`: escolher ate completar 6 membros, antes da validacao
    final do Agente C;
  - `corrigir_equilibrio`: escolher 1 Pokemon por iteracao para reduzir uma
    lacuna prioritaria.

Diretriz:

- usar `rank_pokemon` para formar grupos de candidatos validos;
- usar `rank_pokemon_moveset` quando golpes forem relevantes para confirmar o
  papel do candidato;
- quando houver empate entre candidatos equivalentes, declarar o criterio de
  desempate ou que houve escolha aleatoria controlada;
- nunca apresentar um candidato da AI como escolha do usuario.

Saida esperada:

- segundo ace selecionado, quando aplicavel, com `source=ai` e `locked=false`;
- candidatos selecionados com `source=ai` e `locked=false`;
- trio pretendido para cada candidato;
- papel pretendido;
- lacuna que cada candidato cobre;
- justificativa objetiva.

## Diretriz de Fluxo de Trabalho

```text
Input do usuario
    -> Agente A coleta dados dos Pokemon informados
    -> Agente B define primeiro trio com ace e estrategia principal
    -> Agente E seleciona ou confirma segundo ace com estrategia distinta
    -> Agente E lista candidatos para completar os dois trios e reduzir fraquezas
    -> Agente A coleta dados dos candidatos escolhidos
    -> Agente B integra candidatos e separa trio principal e trio complementar
    -> Agente C valida regras, repeticoes, itens, dois aces e coesao estrategica
        -> se a validacao falhar:
            -> Agente E seleciona substitutos ou ajustes para a lacuna apontada
            -> Agente A coleta dados adicionais
            -> Agente B atualiza a proposta
            -> Agente C revalida
    -> Agente D audita tipos, velocidades, ataque, defesa e fraquezas de cada trio e do time completo
        -> se houver fraquezas relevantes ou trios pouco distintos:
            -> Agente E seleciona M Pokemon ou 1 substituto para corrigir lacunas
            -> Agente A coleta dados dos novos candidatos
            -> Agente B atualiza a proposta
            -> Agente C revalida
            -> Agente D reaudita
        -> se nao houver fraquezas bloqueantes:
            -> finalizar resposta
```

## Condicoes de Encerramento

O fluxo so deve encerrar quando:

- o time tiver exatamente 6 Pokemon;
- o time estiver separado em dois trios de 3 Pokemon;
- houver dois aces identificados, cada um com estrategia diferente;
- os trios forem complementares sem perder identidades distintas;
- todos os Pokemon do usuario tiverem sido preservados ou registrados como
  pendencia;
- cada Pokemon selecionado pela AI tiver papel, motivo e lacuna coberta;
- riscos e incertezas relevantes estiverem declarados;
- o formato final seguir `docs/padrao-agentico-times.md`.

## Condicoes de Bloqueio

O fluxo deve parar e pedir confirmacao quando:

- um Pokemon informado pelo usuario nao puder ser identificado;
- restricoes do usuario tornarem impossivel completar 6 membros validos;
- restricoes do usuario impedirem a escolha de dois aces ou duas estrategias distintas;
- a fonte PokeAPI compativel estiver indisponivel e dados reais forem
  necessarios;
- houver conflito entre preservar escolhas fixas e cumprir uma restricao
  explicita do usuario.
