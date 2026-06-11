# Agentic Pattern For Team Assembly

This document defines how an AI should build a six-Pokemon team when the user provides N desired Pokemon. The goal is to preserve the user's choices, complete the team coherently, and explain the composition in a consistent structure.

When the team is assembled through a multi-agent flow, also use `docs/agentic-team-flow.md`, which defines agents A-E, their responsibilities, and the validation/refinement cycle.

## Objective

The AI receives an initial list of Pokemon chosen by the user and returns a complete team with exactly six Pokemon.

```text
input: N Pokemon desired by the user, where 0 <= N <= 6
output: 6 structured Pokemon, with N fixed by the user and 6 - N selected by the AI
```

## General Rules

- The final team must have exactly six Pokemon.
- The team must be structured as two trios of three Pokemon.
- Each trio must have its own ace and a distinct strategy.
- The two trios must be complementary in the complete team, while staying distinct enough to provide different competitive routes.
- When the user provides only one ace or one strategy, the AI must preserve that ace as fixed and select a second ace with a different strategy for the complementary trio.
- Pokemon chosen by the user are priority choices and must be preserved in the provided order.
- If the user provides more than six Pokemon, use only the first six and state that the limit was applied.
- If the user repeats a Pokemon, keep only the first occurrence and complete the remaining slots.
- Do not invent Pokemon, types, abilities, moves, stats, or items.
- When data is needed, use the available project tools or a PokeAPI-compatible source.
- When data or game-rule uncertainty remains, state the uncertainty instead of filling it with assumptions.

## User-Provided Pokemon

Pokemon provided by the user must be treated as fixed choices, not disposable suggestions.

For each user-selected Pokemon, the AI must structure:

- `name`: canonical name or queryable identifier.
- `source`: `user`.
- `locked`: `true`.
- `reason`: why it was preserved, usually "User-provided choice".
- `role`: team role, when it can be inferred.
- `notes`: important observations such as coverage, redundancy, or gaps.

If a provided Pokemon cannot be found or validated, the AI must:

- keep the provided name in a pending section;
- avoid inventing data for it;
- ask for confirmation or suggest querying again with another identifier.

## AI Pokemon Selection

Open slots must be filled by the AI until the team reaches six members.

Each AI-selected Pokemon must include:

- `source`: `ai`.
- `locked`: `false`.
- `reason`: objective reason for the choice.
- `role`: intended role in the team.
- `replaces_gap`: gap it helps cover.

Selection may be called random only when there is a real choice among valid candidates. Even then, randomness must be controlled by criteria.

Recommended order:

1. Identify the types and roles of the user's fixed Pokemon.
2. Define the first ace and its main strategy.
3. Select or confirm a second ace with a different strategy.
4. Build two trios of three Pokemon, each with one ace and two supports.
5. Identify gaps in each trio and in the complete team.
6. Create a set of valid candidates for each gap.
7. Choose candidates that preserve each trio's identity and reduce the most gaps in the complete team.
8. When equivalent candidates tie, select randomly or state the tie-break criterion.

## Trio Structure

The team must contain:

- `primary_trio`: includes the user-provided ace when one exists, its main strategy, and two Pokemon that enable, protect, or expand that plan.
- `complementary_trio`: includes a second ace, a strategy different from the primary strategy, and two Pokemon that sustain the second plan.

The two strategies must not be only cosmetic variations of the same plan. Real differences include weather vs setup, bulky balance vs speed control, special wallbreak vs physical cleanup, hazards vs offensive pivoting, or stall/burn control vs hyper offense.

The trios must complement each other in the complete team. One trio can cover the other's defensive weaknesses, provide hazard control, open a route for the other ace, offer a different endgame path, or absorb bad matchups for the main strategy.

## Composition Criteria

The AI should aim for practical balance, not absolute competitive perfection.

Priorities:

- Two aces with different strategies and clearly explained roles.
- Two identifiable trios, each with its own plan.
- Complementarity between the trios without merging both into one strategy.
- Offensive and defensive type coverage.
- Avoid excessive shared weaknesses.
- Include a mix of physical and special attackers.
- Include at least one more durable Pokemon when possible.
- Avoid six Pokemon with the same role.
- Consider status or support move utility when move data is available.
- Consider held items when the request involves itemization.

When project tools are available:

- Use `build_pokemon_team` when you need a structured and validated base for completing a six-Pokemon team in two trios.
- Use `rank_pokemon` to find good candidates by type or stat profile.
- Use `rank_pokemon_moveset` to evaluate a candidate's moves.
- Use `get_type_relations` to audit offensive and defensive type interactions.
- Use `list_items` to query general items, categories, and descriptions.

## Call-Depth Decision Guide

Use the lowest number of tool calls that satisfies the user's request and the required validation depth.

1. **One call: basic completion**
   - Use `build_pokemon_team` when the user asks for a complete team and does not require detailed moveset, item, or matchup validation.
   - Stop after this call if the output is complete and pending issues are acceptable for the request.
2. **Two calls: focused candidate validation**
   - Add `rank_pokemon` when the user asks for candidate comparison, a specific type/profile, or a replacement for a known gap.
3. **Three calls: moveset confidence**
   - Add `rank_pokemon_moveset` for an ace or uncertain candidate when the user asks about offensive fit, best moves, or damage-class alignment.
4. **Four calls: type audit**
   - Add `get_type_relations` when the user asks about weaknesses, resistances, immunities, or defensive balance.
5. **Five calls: itemization or final correction**
   - Add `list_items` when the request involves held items, or use one additional focused tool call to correct a prioritized weakness found during validation.

Do not use all five calls by default. A simple request should stay at one call. Increase call depth only when the user's request, pending issues, or validation findings justify it.

## `build_pokemon_team` Tool Contract

The `build_pokemon_team` tool performs the initial team assembly deterministically and returns JSON-serializable data. It accepts:

- `pokemon`: optional list of names or IDs chosen by the user;
- `aces`: optional list with up to two names or IDs that should lead the trios;
- `primary_strategy`: optional strategy for the primary trio;
- `complementary_strategy`: optional strategy for the complementary trio.

The response follows this document's general structure and includes:

- `team_size`: always 6;
- `is_complete`: whether six validated members were selected;
- `user_requested`: normalized Pokemon after duplicate handling and the six-Pokemon limit;
- `team_structure`: strategies for the `primary` and `complementary` trios;
- `team`: members with `name`, `source`, `locked`, `role`, `trio`, `reason`, `notes`, and, for AI choices, `replaces_gap`;
- `analysis`: strengths, trio differences, complementarity, risks, and selection criteria;
- `pending`: unresolved data, duplicates, applied limits, fetch failures, or insufficient candidates.

The tool is not a full competitive simulator. Held items, final movesets, controlled randomness, and competitive-format fine-tuning remain later validation scope when the user asks for that level of detail.

## Suggested Roles

Use these roles as standard vocabulary:

- `physical-attacker`: physical attacker.
- `special-attacker`: special attacker.
- `mixed-attacker`: mixed attacker.
- `physical-wall`: physically durable Pokemon.
- `special-wall`: specially durable Pokemon.
- `support`: support, control, or status role.
- `speed-control`: speed, priority, or pace-control focus.
- `type-coverage`: choice made primarily for type coverage.
- `flex`: flexible role when data is insufficient.

## Response Structure

The AI should respond with this structure:

```text
Final team
Primary trio - strategy=...
1. Pokemon - source=user|ai - role=ace|...
   Reason: ...
   Notes: ...

Complementary trio - strategy=...
4. Pokemon - source=user|ai - role=ace|...
   Reason: ...
   Notes: ...

Team analysis
- Strengths: ...
- Difference between trios: ...
- How the trios complement each other: ...
- Gaps or risks: ...
- Completion criterion: ...

Pending
- Missing data, uncertainties, or confirmations needed.
```

When another agent or system needs to consume the answer, use JSON:

```json
{
  "team_size": 6,
  "user_requested": ["pokemon-a"],
  "team_structure": {
    "primary_trio_strategy": "strategy-a",
    "complementary_trio_strategy": "strategy-b"
  },
  "team": [
    {
      "name": "pokemon-a",
      "source": "user",
      "locked": true,
      "role": "ace",
      "trio": "primary",
      "reason": "User-provided choice.",
      "notes": []
    },
    {
      "name": "pokemon-b",
      "source": "ai",
      "locked": false,
      "role": "type-coverage",
      "trio": "complementary",
      "reason": "Covers a team type gap.",
      "replaces_gap": "defensive coverage",
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

## Explanation Rules

- Explain why each AI-selected Pokemon was chosen.
- Explain who the two aces are and what strategy each one leads.
- Explain how the two trios are distinct and how they complement each other.
- Clearly distinguish user choices from AI choices.
- Do not present AI-selected Pokemon as if they were user choices.
- If selection is random among equivalent candidates, state which criteria formed the candidate group.
- Avoid responses that only list names; always include role and justification.

## Example

User input:

```text
I want to build a team with pikachu and charizard.
```

Expected response:

```text
Final team
Primary trio - strategy=electric coverage and speed pressure
1. pikachu - source=user - role=ace
   Reason: User-provided choice.
   Notes: Can act as a fast Electric attacker.

2. pokemon-b - source=ai - role=speed-control
   Reason: Supports the first ace's strategy.
   Notes: Helps maintain offensive pace.

3. pokemon-c - source=ai - role=physical-wall
   Reason: Completes a defensive gap in the primary trio.
   Notes: Chosen from durable candidates.

Complementary trio - strategy=special wallbreak with defensive support
4. charizard - source=user - role=ace
   Reason: User-provided choice.
   Notes: Leads the team's second offensive route.

5. pokemon-d - source=ai - role=support
   Reason: Sustains the second ace's strategy.
   Notes: Helps protect the complementary trio.

6. pokemon-e - source=ai - role=type-coverage
   Reason: Covers shared weaknesses between the trios.
   Notes: Also creates safe entry for the primary trio.

Team analysis
- Strengths: Electric and Fire coverage is already started by the user's Pokemon.
- Difference between trios: the first trio plays through speed; the second plays through special wallbreaking.
- How the trios complement each other: one trio pressures fast checks while the other breaks durable defenders.
- Gaps or risks: check shared weaknesses before confirming the four remaining members.
- Completion criterion: preserve fixed choices, reduce repeated weaknesses, and balance roles.

Pending
- Validate final data with tools before locking movesets and items.
```
