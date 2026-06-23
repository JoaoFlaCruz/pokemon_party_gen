---
name: create-single-team
description: Use when any AI agent needs to orchestrate creation of one six-Pokemon single battle team with two three-Pokemon trios, calling list-pokemon for candidates, create-pokemon for selected Pokemon packages, and evaluate-single-team for revision cycles before returning a formatted JSON team.
argument-hint: "<primary-ace> | <primary-strategy> | [initial-trio] | [second-ace-or-complementary-strategy] | [constraints]"
---

# Create Single Team

## Description, Usage, And Examples

Orchestrate the creation of one complete six-Pokemon single battle team. This
skill is the main coordinator in the new architecture: it uses `list-pokemon` to
find possible candidates for requested or complementary strategies, uses
`create-pokemon` to build each selected Pokemon package, and uses
`evaluate-single-team` to critique the draft in revision cycles before returning
the final formatted JSON team.

This skill does not fetch Pokemon facts directly. Factual candidate discovery,
Pokemon set creation, move data, item data, legality checks, and type checks must
be delegated to the sub-skills and their allowed MCP tools.

Usage:

```text
create-single-team <primary-ace> | <primary-strategy> | [initial-trio] | [second-ace-or-complementary-strategy] | [constraints]
```

Examples:

```text
create-single-team Charizard | sun special offense | | bulky hazard balance | champions_only=true
create-single-team Garchomp | physical setup sweeper | Garchomp, Rotom-Wash | speed control | no duplicate items
create-single-team Archaludon | rain offense | | choose complementary strategy | preserve locked user Pokemon
```

## Inputs

Before building a team, obtain or infer only from the user request:

- `primary_ace`: required Pokemon that leads the primary trio.
- `primary_strategy`: required strategy or function for the primary ace/trio.
- `initial_trio`: optional user-provided Pokemon that must be preserved as locked
  members when present.
- `second_ace_or_complementary_strategy`: optional user-provided second ace or
  second strategy. If absent, select a complementary strategy and candidate ace
  through `list-pokemon`.
- `constraints`: optional rules such as Champions-only, no duplicate items,
  banned Pokemon, preserve locked Pokemon, preferred type, physical/special
  leaning, or matchup priorities.

If `primary_ace` or `primary_strategy` is missing, ask for the missing value. Do
not build the team without both.

## Architecture Boundary

Use only these local skills for orchestration work:

- `list-pokemon`: candidate discovery for strategies, roles, type needs, stat
  profiles, team gaps, and complementary trio planning.
- `create-pokemon`: creation of each final Pokemon package after a candidate is
  selected.
- `evaluate-single-team`: unstructured critique of a drafted team and revision
  demands before finalization.

Do not call MCP tools directly from this orchestration skill. Do not use memory,
web search, direct PokeAPI calls, local source-code assumptions, CLIs, Python
imports, tests, fixture files, `build_pokemon_team`, or `search_champions_strategy`
to fill Pokemon facts. If a sub-skill reports missing data or `tool_unavailable`,
carry that into `pending` and either revise around it or stop with a blocked JSON
result.

## Orchestration Steps

1. Normalize the request into primary ace, primary strategy, optional initial
   trio, optional second ace or complementary strategy, and constraints.
2. Mark all user-provided Pokemon as locked. Locked Pokemon must remain in the
   team unless the user explicitly confirms replacement.
3. Define the primary trio plan:
   - keep the primary ace in the primary trio;
   - if the user provided initial-trio partners, preserve them when possible;
   - otherwise call `list-pokemon` for primary-strategy support roles, type
     coverage, speed control, durability, utility, or other gaps.
4. Define the complementary trio plan:
   - if the user provided a second ace, preserve it as the complementary ace;
   - if the user provided only a complementary strategy, call `list-pokemon` to
     find a second ace for that strategy;
   - if neither was provided, infer a complementary strategy that differs from
     the primary plan and call `list-pokemon` for candidates.
5. Use `list-pokemon` for every open slot or major gap. Requests should be
   strategy-specific, for example: defensive pivot, speed control, physical
   wallbreaker, special wallbreaker, hazard control, status utility, type check,
   win condition, or bulky support.
6. Select six Pokemon total, split into two trios of three. Selection must favor:
   - one ace per trio;
   - distinct strategies between trios;
   - low harmful repetition of types, roles, key-stat focus, and moves;
   - complementary offensive, defensive, and utility coverage;
   - preservation of locked user choices.
7. Call `create-pokemon` for each selected Pokemon with its chosen role/strategy,
   item if fixed or strategically required, and key stat. Use the returned JSON
   packages as the only source for final member data.
8. Assemble a draft team JSON from the six `create-pokemon` packages.
9. Call `evaluate-single-team` with the draft, primary strategy, complementary
   strategy, and constraints.
10. Read the evaluator's unstructured feedback blocks and perform a revision
    cycle when feedback says `revise` or identifies blockers that can be fixed:
    - use `list-pokemon` when the feedback asks for a replacement, more
      versatility, different type, different role, or different key-stat profile;
    - use `create-pokemon` when the feedback asks to revise a set, diversify
      moves, change item, adjust role, or complete missing member fields;
    - preserve locked Pokemon unless feedback says user confirmation is required.
11. Repeat evaluation after each meaningful revision. Stop when the evaluator
    indicates acceptance, when no further supported revision is available, or when
    the maximum cycle count is reached.
12. Return one formatted JSON object with the final team, evaluation history, and
    pending issues.

## Cycle Control

Use bounded revision cycles:

- Maximum evaluation cycles: 3.
- Do not repeat the same failed revision without new information.
- Prefer one high-impact revision per cycle.
- Stop early when the team is accepted.
- Stop with `status="blocked"` when locked user choices, unavailable tools, or
  missing data prevent a complete validated team.
- Stop with `status="needs_user_confirmation"` when the best fix requires
  replacing or changing a locked user Pokemon.

## Required Final JSON Output

Always return a formatted JSON object. Do not return prose instead of JSON. The
final package must use this shape:

```json
{
  "status": "accepted|revised|blocked|needs_user_confirmation",
  "premises": {
    "primary_ace": "pokemon-name",
    "primary_strategy": "strategy",
    "complementary_ace": "pokemon-name-or-null",
    "complementary_strategy": "strategy-or-null",
    "constraints": [],
    "locked_pokemon": ["pokemon-name"]
  },
  "team_structure": {
    "team_size": 6,
    "primary_trio_strategy": "strategy",
    "complementary_trio_strategy": "strategy",
    "primary_trio": ["pokemon-a", "pokemon-b", "pokemon-c"],
    "complementary_trio": ["pokemon-d", "pokemon-e", "pokemon-f"]
  },
  "team": [
    {
      "slot": 1,
      "trio": "primary",
      "role": "ace",
      "pokemon": {
        "name": "pokemon-name",
        "ability": "ability-name-or-null",
        "item": "item-name-or-null",
        "nature": "nature-name",
        "types": ["type-a"],
        "moves": [],
        "added_points": {
          "hp": 0,
          "attack": 0,
          "defense": 0,
          "special_attack": 0,
          "special_defense": 0,
          "speed": 0
        },
        "metadata": {},
        "validation": {},
        "pending": []
      }
    }
  ],
  "selection_log": [
    {
      "step": "list-pokemon|create-pokemon|evaluate-single-team|orchestrator",
      "purpose": "why this step was used",
      "result": "short summary"
    }
  ],
  "evaluation_history": [
    {
      "cycle": 1,
      "feedback_summary": "short summary of evaluator feedback",
      "action_taken": "revision made or reason no revision was possible"
    }
  ],
  "analysis": {
    "primary_plan": "how the primary trio wins or creates pressure",
    "complementary_plan": "how the complementary trio differs",
    "trio_complementarity": "how the trios help each other",
    "versatility_notes": "how repeated types, roles, stats, and moves were handled",
    "risks": []
  },
  "validation": {
    "complete": false,
    "evaluation_cycles": 0,
    "accepted_by_evaluator": false,
    "blocking_pending": false
  },
  "pending": []
}
```

## Finalization Rules

- Return exactly six Pokemon when `status` is `accepted` or `revised`.
- Each final member must come from a `create-pokemon` JSON package.
- Every final Pokemon must have exactly four moves in its package unless the team
  is returned as `blocked` or `needs_user_confirmation` with pending issues.
- Preserve all locked user Pokemon in the final team.
- Include evaluator feedback summaries in `evaluation_history`, not the entire
  private reasoning transcript.
- Include unresolved sub-skill pending issues in top-level `pending` when they
  affect the team.
- Do not claim `accepted_by_evaluator=true` unless `evaluate-single-team`
  indicated the team should be accepted.

## Revision Priorities

When evaluation demands revision, prioritize in this order:

1. Fix structural blockers: team size, trio split, missing ace, duplicate Pokemon,
   or locked Pokemon violation.
2. Fix member completeness blockers reported by `create-pokemon` packages.
3. Improve strategy distinction between primary and complementary trios.
4. Improve versatility by reducing harmful repetition of types, functions,
   key-stat focus, and repeated moves.
5. Improve type, speed, physical/special, defensive, item, and utility balance.
6. Preserve strong pieces identified by the evaluator.

## Limits

- Do not fetch or invent factual Pokemon data directly; delegate to sub-skills.
- Do not call MCP tools directly from this orchestrator.
- Do not call `build_pokemon_team` or `search_champions_strategy`.
- Do not silently replace locked user Pokemon.
- Do not return unstructured prose as the final answer; the final answer must be
  formatted JSON.
- Do not exceed three evaluation cycles unless the user explicitly asks for a
  deeper revision loop.
