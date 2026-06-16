# Agentic Pattern For Team Assembly

This document defines how an AI should build a six-Pokemon team when the user provides N desired Pokemon. The goal is to preserve the user's choices, complete the team coherently, and explain the composition in a consistent structure.

When the team is assembled through a multi-agent flow, also use `docs/agentic-team-flow.md`, which defines agents A-F, their responsibilities, and the validation/refinement cycle.

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
- Pokemon selected by the AI must come from the Pokemon Champions library when project tools provide candidate selection.
- If the user provides more than six Pokemon, use only the first six and state that the limit was applied.
- If the user repeats a Pokemon, keep only the first occurrence and complete the remaining slots.
- Do not invent Pokemon, types, abilities, moves, stats, or items.
- When data is needed, use the available project tools or a PokeAPI-compatible source.
- When data or game-rule uncertainty remains, state the uncertainty instead of filling it with assumptions.
- A final team may be accepted only when every final Pokemon has the complete member fields defined in this document. If any required field cannot be validated or strategy-justified, stop with `pending` instead of presenting the Pokemon as complete.

## User-Provided Pokemon

Pokemon provided by the user must be treated as fixed choices, not disposable suggestions.

For each user-selected Pokemon, the AI must structure:

- `name`: canonical name or queryable identifier.
- `source`: `user`.
- `locked`: `true`.
- `reason`: why it was preserved, usually "User-provided choice".
- `role`: team role.
- `trio`: `primary` or `complementary`.
- `moves`: exactly four validated moves, each with a strategic reason.
- `evs`: named stat allocations with point values and strategic justification.
- `nature`: recommended nature justified by role and strategy.
- `item`: recommended held item validated from available item data or explicitly supported by the project data context.
- `usage_suggestion`: concise guidance for the Pokemon in the team strategy.
- `notes`: important observations such as coverage, redundancy, or gaps.

If a provided Pokemon cannot be found or validated, the AI must:

- keep the provided name in a pending section;
- avoid inventing data for it;
- ask for confirmation or suggest querying again with another identifier.
- avoid presenting it as a complete final team member until validation succeeds.

## AI Pokemon Selection

Open slots must be filled by the AI until the team reaches six members. AI-selected Pokemon must be selected from the Pokemon Champions library; if the library data is unavailable or too narrow to complete the team, report the pending issue instead of using unrestricted candidates silently.

Each AI-selected Pokemon must include:

- `source`: `ai`.
- `locked`: `false`.
- `reason`: objective reason for the choice.
- `role`: intended role in the team.
- `trio`: `primary` or `complementary`.
- `replaces_gap`: gap it helps cover.
- `moves`: exactly four validated moves, each with a strategic reason.
- `evs`: named stat allocations with point values and strategic justification.
- `nature`: recommended nature justified by role and strategy.
- `item`: recommended held item validated from available item data or explicitly supported by the project data context.
- `usage_suggestion`: concise guidance for the Pokemon in the team strategy.

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

- Use `rank_pokemon` to find AI-selected candidates by type or stat profile. The MCP tool defaults to Pokemon Champions scope with `champions_only=true`; pass `champions_only=false` only when the request explicitly needs a broader non-Champions ranking.
- Use `rank_pokemon_moveset` to evaluate a candidate's moves.
- Use `get_type_relations` to audit offensive and defensive type interactions.
- Use `list_items` to query general items, categories, and descriptions.
- Use `validate_champions_legality` to validate Pokemon, move, ability, or item facts in Pokemon Champions scope.
- For strategic roles such as rain setter, rain attacker, defensive pivot, coverage check, speed control, or win condition, construct the role criteria inside the agentic flow and prove them with lower-level tools. Do not offload role selection to a public strategy-search tool. Use source-backed filters, focused legality checks, moveset checks, and type relations to support the final team.

## Call-Depth Decision Guide

Use the lowest number of tool calls that satisfies the user's request and the required validation depth.

1. **One call: basic completion**
   - Use `rank_pokemon` when open slots need data-backed candidates and the user does not require detailed moveset, item, or matchup validation.
   - Stop after this call if the candidate data is enough for the AI to complete and explain the team.
2. **Two calls: focused candidate validation**
   - Add a second focused `rank_pokemon`, `rank_pokemon_moveset`, or `get_type_relations` call when the user asks for comparison, a specific profile, or validation of a known gap.
3. **Three calls: moveset confidence**
   - Add `rank_pokemon_moveset` for an ace or uncertain candidate when the user asks about offensive fit, best moves, or damage-class alignment.
4. **Four calls: type audit**
   - Add `get_type_relations` when the user asks about weaknesses, resistances, immunities, or defensive balance.
5. **Five calls: itemization or final correction**
   - Add `list_items` when the request involves held items, or use one additional focused tool call to correct a prioritized weakness found during validation.

Do not use all five calls by default. A simple request should stay at one call. Increase call depth only when the user's request, pending issues, or validation findings justify it. `build_pokemon_team` is not an active project tool; full team assembly is an AI responsibility using validated lower-level data.

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

## Detailed Set Population

Agent F must populate final set details after the team members, roles, trio strategies, and main risks are stable.

For each final Pokemon, include:

- `moves`: exactly four moves, each with a reason explaining its strategic purpose.
- `evs`: named stat allocations with point values.
- `nature`: recommended nature.
- `item`: recommended held item.
- `usage_suggestion`: concise guidance for using the Pokemon in the team strategy.

Agent F must not invent moves, EVs, natures, or items. If a detail cannot be validated or confidently justified from available data, record the unresolved field in `pending` instead of filling it with unsupported content.

## Complete Member Contract

A final Pokemon member is complete only when it has:

- `name`, `source`, `locked`, `role`, `trio`, and `reason`.
- exactly four `moves`, each with `name` and `reason`.
- `evs`, with named stats and point values.
- `nature`.
- `item`.
- `usage_suggestion`.
- `notes`, even when the list is empty.
- `replaces_gap` for AI-selected Pokemon.

Identity, stats, Champions membership, type, move, and item facts must come from project tools, a PokeAPI-compatible source, or injected fakes in tests. EVs, nature, held item choice, and usage guidance are strategic recommendations, so they must be tied to the Pokemon role, trio strategy, stats, moves, or team need.

Do not use the final team format for incomplete members. If any required field is missing and an available tool can fill it, make one focused data request through the agentic flow. If the data remains unavailable or cannot be justified, return the best validated partial result with `pending` instead of choosing `accept`.

When a tool returns structured diagnostics, preserve the useful diagnostic fields in `pending`: `code`, `message`, `entity`, `missing_fields`, `source`, `details`, and whether it is blocking. Common diagnostic codes include `pokemon_not_found`, `outside_champions_scope`, `incomplete_data`, `source_unavailable`, `unsupported_validation`, and `no_eligible_candidates`.

For weather or other mechanic-specific teams, do not infer setters, abusers, legality, or item support from outside knowledge. Use legality, ranking, moveset, item, and type tools to prove the strategy criteria inside the A-F flow. Internal case criteria must be structured, limited to project-supported primitives, and as complete as the validated information allows; invalid or under-specified criteria go to `pending`.

## Reflection And Finalization

Before presenting the final team, run a concise reflection checkpoint. The checkpoint should decide one of:

- `accept`: present the team because it satisfies the request, preserves user choices, has six complete validated members, and has two distinct trios with two distinct aces.
- `refine`: make one more focused improvement because a specific candidate, moveset, type, item, or correction call is expected to improve the recommendation.
- `ask_user`: stop and ask for clarification because user constraints are ambiguous, conflict with fixed Pokemon, or require a preference that cannot be inferred.
- `stop_with_pending`: present the best validated result with pending issues because data is unavailable, constraints prevent a confident complete team, or another call would not change the recommendation.

Reflection must preserve locked user Pokemon. If a user-selected Pokemon creates a weakness, correct around it unless the user explicitly confirms replacement. Do not keep refining by repeating the same kind of call without new information; stop at the lowest call count that satisfies the request and validation needs.

The final reflection must include the complete member contract. If any final Pokemon is missing a required field, the decision cannot be `accept`; choose `refine` when one focused data request can fill the gap, `ask_user` when user confirmation is required, or `stop_with_pending` when the data source cannot support a complete result.

The final response should expose only the useful result of reflection: relevant risks, unresolved data, needed user confirmation, or why the team is ready. It should not include a long private reasoning transcript.

## Response Structure

The AI should respond with this structure:

```text
Final team
Primary trio - strategy=...
1. Pokemon - source=user|ai - role=ace|...
   Motivo: ...
   Golpes:
   - Move A: ...
   - Move B: ...
   - Move C: ...
   - Move D: ...
   EVs: stat-a XXX pts + stat-b XXX pts + stat-c XXX pts
   Natureza: ...
   Item: ...
   Sugestao: ...
   Notes: ...

Complementary trio - strategy=...
4. Pokemon - source=user|ai - role=ace|...
   Motivo: ...
   Golpes:
   - Move A: ...
   - Move B: ...
   - Move C: ...
   - Move D: ...
   EVs: stat-a XXX pts + stat-b XXX pts + stat-c XXX pts
   Natureza: ...
   Item: ...
   Sugestao: ...
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
      "moves": [
        {"name": "move-a", "reason": "Supports the primary strategy."},
        {"name": "move-b", "reason": "Provides coverage."},
        {"name": "move-c", "reason": "Improves utility."},
        {"name": "move-d", "reason": "Supports the endgame plan."}
      ],
      "evs": [
        {"stat": "speed", "points": 252},
        {"stat": "special-attack", "points": 252},
        {"stat": "hp", "points": 4}
      ],
      "nature": "timid",
      "item": "held-item-a",
      "usage_suggestion": "Use as the primary pressure point for the first trio.",
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
      "moves": [
        {"name": "move-e", "reason": "Matches the assigned role."},
        {"name": "move-f", "reason": "Covers a relevant matchup."},
        {"name": "move-g", "reason": "Adds team utility."},
        {"name": "move-h", "reason": "Supports the complementary strategy."}
      ],
      "evs": [
        {"stat": "hp", "points": 252},
        {"stat": "defense", "points": 252},
        {"stat": "special-defense", "points": 4}
      ],
      "nature": "bold",
      "item": "held-item-b",
      "usage_suggestion": "Use to cover the defensive gap and support the complementary trio.",
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
- Clearly state when a preserved user choice is outside the Pokemon Champions library.
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
   Motivo: User-provided choice.
   Golpes:
   - thunderbolt: Main Electric pressure.
   - move-b: Coverage or utility, if validated.
   - move-c: Coverage or utility, if validated.
   - move-d: Coverage or utility, if validated.
   EVs: speed 252 pts + special-attack 252 pts + hp 4 pts
   Natureza: timid
   Item: held item, if validated.
   Sugestao: Use as a fast Electric attacker that pressures early openings.
   Notes: Can act as a fast Electric attacker.

2. pokemon-b - source=ai - role=speed-control
   Motivo: Supports the first ace's strategy.
   Golpes:
   - move-a: Speed-control purpose.
   - move-b: Coverage purpose.
   - move-c: Utility purpose.
   - move-d: Endgame purpose.
   EVs: speed 252 pts + attack 252 pts + hp 4 pts
   Natureza: role-aligned nature.
   Item: role-aligned item.
   Sugestao: Use to keep offensive pace for the primary trio.
   Notes: Helps maintain offensive pace.

3. pokemon-c - source=ai - role=physical-wall
   Motivo: Completes a defensive gap in the primary trio.
   Golpes:
   - move-a: Defensive utility.
   - move-b: Reliable damage.
   - move-c: Team support.
   - move-d: Coverage or recovery.
   EVs: hp 252 pts + defense 252 pts + special-defense 4 pts
   Natureza: defensive nature.
   Item: defensive item.
   Sugestao: Use to absorb physical pressure and create safe turns.
   Notes: Chosen from durable candidates.

Complementary trio - strategy=special wallbreak with defensive support
4. charizard - source=user - role=ace
   Motivo: User-provided choice.
   Golpes:
   - move-a: Main Fire pressure.
   - move-b: Secondary STAB or coverage.
   - move-c: Setup or utility.
   - move-d: Coverage or endgame option.
   EVs: speed 252 pts + special-attack 252 pts + hp 4 pts
   Natureza: role-aligned nature.
   Item: role-aligned item.
   Sugestao: Use as the second route for offensive pressure.
   Notes: Leads the team's second offensive route.

5. pokemon-d - source=ai - role=support
   Motivo: Sustains the second ace's strategy.
   Golpes:
   - move-a: Support purpose.
   - move-b: Protection or control.
   - move-c: Coverage or utility.
   - move-d: Recovery or pivoting.
   EVs: hp 252 pts + special-defense 252 pts + defense 4 pts
   Natureza: support nature.
   Item: support item.
   Sugestao: Use to protect the complementary ace and keep the plan stable.
   Notes: Helps protect the complementary trio.

6. pokemon-e - source=ai - role=type-coverage
   Motivo: Covers shared weaknesses between the trios.
   Golpes:
   - move-a: Coverage purpose.
   - move-b: Secondary coverage.
   - move-c: Utility purpose.
   - move-d: Endgame or pivoting option.
   EVs: attack 252 pts + speed 252 pts + hp 4 pts
   Natureza: coverage-aligned nature.
   Item: coverage-aligned item.
   Sugestao: Use to switch into shared risks and create momentum.
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
