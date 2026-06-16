# Agentic Flow For Pokemon Teams

This document defines six support agents for assembling six-Pokemon teams and the workflow guideline based on this project's agentic process. It complements `docs/agentic-team-pattern.md`, aligns with the diagram in `docs/agentic-team-flow.pdf`, and should be used when an AI needs to transform initial user choices into a complete, validated, and explained team.

## Input

The minimum flow input is:

- names or identifiers of Pokemon chosen by the user;
- desired battle strategy, when provided;
- second ace or second strategy, when provided;
- additional restrictions, when present, such as type, role, item, generation, or physical/special preference.

Pokemon provided by the user are fixed members. The flow may validate, classify, and flag risks for those Pokemon, including whether they are outside the Pokemon Champions library, but it must not remove them without explicit confirmation. When the user provides only one ace, the flow must preserve it as the first ace and select a second ace with a distinct strategy to lead the complementary trio.

## Agent A: Data Collector

Responsibilities:

- fetch data for user-provided Pokemon or candidates;
- fetch available moves and move data;
- fetch held or general item data when the strategy involves itemization;
- fetch type relations when another agent needs to evaluate coverage or weaknesses.
- fulfill focused data requests from later agents when a required final member field is missing and the data is expected to be available from a project tool.

Recommended tools:

- `rank_pokemon`, to identify Pokemon Champions candidates by type or stat profile;
- `rank_pokemon_moveset`, to evaluate offensive moves for one Pokemon;
- `list_items`, to query general items and descriptions;
- `get_type_relations`, to query offensive and defensive type relations.
- `validate_champions_legality`, to validate Pokemon, moves, abilities, and items against Champions scope and report structured blockers.

Expected output:

- structured and traceable data;
- indication of missing or unresolved data;
- no invented stats, types, moves, abilities, or items.
- explicit confirmation of which required final member fields the data can support.
- structured diagnostics for missing legality, strategy-role, Pokemon, move, ability, item, or source data.

## Agent B: Base Builder

Responsibilities:

- build a first playable proposal based on the strategy;
- preserve user Pokemon as `source=user` and `locked=true`;
- define two trios of three Pokemon, each with its own ace and strategy;
- select or confirm a second ace when the user provides only one;
- fill probable roles for each member;
- propose provisional moveset, ability, stat distribution, and item only when data has been validated and the draft needs them before Agent F;
- make explicit any gaps that still need candidates from Agent E.

Guidelines:

- if the team has fewer than six Pokemon, work with open slots;
- if the user provides more than six Pokemon, keep only the first six and record that the limit was applied;
- avoid making the first proposal depend on data that Agent A has not validated.

Expected output:

- team draft separated into primary and complementary trios;
- two aces identified with different strategies;
- suggested roles;
- provisional moveset, ability, stat distribution, and item when needed before final set population;
- known initial gaps.

## Agent C: Strategic Validator

Responsibilities:

- validate general team-building rules;
- check duplicate Pokemon, duplicate items when items are used, invalid members, and the six-Pokemon limit;
- evaluate whether role and stat distribution supports the declared or selected strategies;
- evaluate whether both trios have their own aces, different strategies, and real complementarity;
- evaluate cohesion among Pokemon, movesets, abilities, items, and strategy;
- execute the reflection step before sending the team to audit or refinement.

Validation criteria:

- exactly six Pokemon in the final result;
- two trios of three Pokemon in the final result;
- two identified aces with distinct strategies;
- user choices preserved;
- reasonable role mix when possible;
- objective justifications for AI-selected Pokemon;
- complete member fields after Agent F runs;
- pending issues declared when data is insufficient.

Expected output:

- status `valid`, `needs_refinement`, or `blocked_by_data`;
- list of required adjustments;
- recommendation to proceed to Agent D, return to Agent B, or call Agent E.

## Agent D: Balance Auditor

Responsibilities:

- check types, weaknesses, resistances, and immunities;
- identify excessive shared weaknesses;
- audit each trio separately, then the complete team;
- evaluate whether one trio covers the other's weaknesses;
- evaluate team speeds, attack stats, and defensive stats;
- evaluate excessive role redundancy;
- identify offensive, defensive, and utility gaps.

Guidelines:

- use Agent A's data and request new type queries when needed;
- state uncertainties instead of assuming unqueried relations;
- distinguish acceptable risk from real blockers.

Expected output:

- team-balance diagnosis;
- prioritized gaps;
- decision `balanced=true|false`.

## Agent E: Candidate Selector

Responsibilities:

- list possible Pokemon from the Pokemon Champions library for open slots;
- select a second ace when the user did not provide one;
- select candidates based on the two trio strategies, gaps, and validated data;
- operate in three modes:
  - `select_second_ace`: choose an ace with a strategy different from the first trio's strategy;
  - `complete_team`: choose members until the team has six Pokemon, before Agent C's final validation;
  - `correct_balance`: choose one Pokemon per iteration to reduce a priority gap.

Guidelines:

- use `rank_pokemon` to form groups of valid Pokemon Champions candidates;
- use `rank_pokemon_moveset` when moves are relevant to confirm the candidate's role;
- when equivalent candidates tie, state the tie-break criterion or that controlled random selection was used;
- never present an AI-selected candidate as a user choice.

Expected output:

- second ace selected, when applicable, with `source=ai` and `locked=false`;
- selected candidates with `source=ai` and `locked=false`;
- intended trio for each candidate;
- intended role;
- gap each candidate covers;
- objective justification.

## Agent F: Set Populator

Responsibilities:

- populate the final detailed set for each Pokemon after team membership, roles, and trio strategies are stable;
- choose or confirm exactly four moves per Pokemon, with one reason per move, when enough validated move data and strategy context are available;
- recommend EV allocations, nature, and held item according to the Pokemon's role, stats, trio strategy, and team needs;
- write a concise usage suggestion explaining how to use the Pokemon in the final strategy;
- request missing move, item, Pokemon, or type data through Agent A when that data is expected to improve the set;
- record missing or uncertain set details in `pending` instead of inventing unsupported moves, EVs, natures, or items;
- run a completeness check for each final Pokemon after set population.

Guidelines:

- run after Agent C and Agent D have validated a stable six-Pokemon draft;
- rerun for any Pokemon affected by a later change to team member, role, trio strategy, or priority gap;
- keep user-selected Pokemon locked while populating their final sets;
- tie EVs and natures to role and strategy, because they are strategic recommendations rather than direct PokeAPI facts;
- stop with pending details when additional data calls would not improve confidence.
- do not present a Pokemon as complete unless it has `name`, `source`, `locked`, `role`, `trio`, `reason`, exactly four moves with reasons, EVs with stat names and point values, nature, item, usage suggestion, notes, and `replaces_gap` for AI selections.

Expected output:

- `moves`: exactly four entries, each with a move name and reason;
- `evs`: named stats with point values;
- `nature`: recommended nature;
- `item`: recommended held item;
- `usage_suggestion`: how to use the Pokemon in the final strategy;
- complete-member status for each Pokemon;
- pending set details when validation or confidence is insufficient.

## Tool Boundary

Full team construction is an AI workflow responsibility, not a dedicated MCP tool. `build_pokemon_team` is not active and must not be used for team construction. Agents must preserve user-selected Pokemon as fixed members, use lower-level tools to gather validated data, choose AI-selected additions from Pokemon Champions candidates returned by `rank_pokemon`, and use Agent F to populate final set details.

## One-To-Five-Call Operating Model

Agents should use the fewest calls needed to satisfy the user request and validation needs.

```text
1 call  -> rank_pokemon
2 calls -> add one focused rank_pokemon, rank_pokemon_moveset, or get_type_relations call
3 calls -> add rank_pokemon_moveset when moveset confidence matters
4 calls -> add get_type_relations for type audit
5 calls -> add list_items or one focused correction call
```

### 1 Call: Complete A Basic Team

Use `rank_pokemon` when the user asks for a complete team and open slots need candidate data but the request does not require detailed validation. This is enough when:

- user choices are clear or pending issues are acceptable;
- Champions-scoped candidates are enough for the AI to complete six members;
- the user did not ask for movesets, itemization, or matchup audit.

### 2 Calls: Compare Or Correct Candidates

Add one focused candidate or validation call when the user asks for alternatives, wants a specific type or stat profile, or when the draft has a gap that needs candidate search.

### 3 Calls: Validate Moveset Fit

Add `rank_pokemon_moveset` for an ace or candidate when offensive role confidence matters. Use it to confirm physical/special alignment, move power, accuracy, and status-move availability.

### 4 Calls: Audit Types

Add `get_type_relations` when the user asks about weaknesses, resistances, immunities, type coverage, or defensive balance. Use it for the most relevant shared weakness or core type first.

### 5 Calls: Itemization Or Final Correction

Add `list_items` when itemization is requested. If items are not relevant, use the fifth call as one focused correction call for the highest-priority issue found by validation.

Do not use all five calls by default. Stop once the request is satisfied, the relevant pending issues are stated, and additional calls would not change the recommendation.

## Champions Strategy And Weather Requests

When the user asks for a Champions-only strategy that depends on a specific mechanic, such as rain with Archaludon, keep strategy construction inside the A-F workflow and use lower-level factual tools before final set population:

1. Use `validate_champions_legality` for fixed Pokemon and key proposed entities when legality or completeness is uncertain.
2. Let Agents B and E formulate the needed roles, such as rain setter, rain attacker, defensive pivot, coverage check, speed control, or win condition, from the user's request and validated facts.
3. Use `rank_pokemon` with type, stat, and speed filters to find Champions-scoped candidates, then use `validate_champions_legality` and `rank_pokemon_moveset` to prove key abilities, moves, and role fit for selected candidates.
4. Use `list_items` and `get_type_relations` to validate final item facts and matchup claims for selected candidates.
5. If the tools return structured diagnostics such as `pokemon_not_found`, `outside_champions_scope`, `incomplete_data`, `source_unavailable`, `unsupported_validation`, or `no_eligible_candidates`, carry those diagnostics into `pending` instead of inferring missing facts externally.

Do not call `search_champions_strategy` as a public shortcut. Strategy cases are an internal reasoning pattern for the AI: the agent should state and validate its role criteria through lower-level tools, while Agent B, C, D, E, and F remain responsible for team construction, validation, auditing, candidate correction, and final set population.

## Reflection Pattern

Reflection is a concise decision checkpoint, not a separate tool call by default. Use it to decide whether the current team is good enough, whether one more focused call can improve it, or whether the user or data source must resolve a blocker.

Use these decisions:

- `accept`: the team satisfies the request, preserves user choices, has six complete validated members, has two distinct trios and aces, and has no blocker that another call is expected to improve.
- `refine`: one specific gap can be improved by one additional candidate, moveset, type, item, or correction call within the 1-to-5-call model.
- `ask_user`: user constraints are ambiguous, conflict with fixed Pokemon, or require a preference that cannot be inferred from validated data.
- `stop_with_pending`: data is unavailable, role evidence cannot be proven after any useful focused validation, constraints prevent a complete confident team, or additional calls would not change the recommendation.

Reflection checkpoints:

1. After the initial team draft, check completion, preserved user choices, Champions-scope pending issues, trio structure, ace distinction, pending issues, and whether the user's request justifies additional calls.
2. After Agent C validates strategy, choose whether to proceed, refine the candidate set, ask the user, or stop with pending issues.
3. After Agent D audits balance, distinguish acceptable risk from a blocker that deserves one focused correction.
4. After Agent F populates set details, run the complete-member validation gate and confirm whether missing Pokemon, move, item, type, Champions, EV, nature, or usage fields require one more data request through Agent A or should be declared in `pending`.
5. Before the final response, confirm the answer satisfies the user request, every final member is complete, and relevant risks, uncertainty, or unresolved data are declared.

Loop-control rules:

- Stop at the lowest call count that satisfies the user's request and validation needs.
- When choosing `refine`, name the highest-priority actionable gap, the next call, and the expected improvement before making that call.
- Correct around user-selected Pokemon unless the user explicitly confirms a replacement.
- Do not repeat the same kind of refinement without new information.
- When the call model is exhausted or another call would not change the recommendation, choose `accept`, `ask_user`, or `stop_with_pending`.
- Never choose `accept` when a final Pokemon is missing a required complete-member field.

## Workflow Guideline

```text
User input
    -> Agent A collects data for provided Pokemon
    -> Agent B defines the first trio with ace and main strategy
    -> Agent E selects or confirms a second ace with a distinct strategy
    -> Agent E lists candidates to complete both trios and reduce weaknesses
    -> Agent A collects data for selected candidates
    -> Agent B integrates candidates and separates primary and complementary trios
    -> Reflection checkpoint:
        -> if decision=refine:
            -> Agent E selects one focused adjustment
        -> if decision=ask_user or decision=stop_with_pending:
            -> stop with the relevant question or pending issue
        -> if decision=accept:
            -> continue
    -> Agent C validates rules, duplicates, items, two aces, and strategic cohesion
    -> Reflection checkpoint:
        -> if decision=refine:
            -> Agent E selects replacements or adjustments for the highest-priority gap
            -> Agent A collects additional data
            -> Agent B updates the proposal
            -> Agent C revalidates
        -> if decision=ask_user or decision=stop_with_pending:
            -> stop with the relevant question or pending issue
        -> if decision=accept:
            -> continue
    -> Agent D audits types, speeds, attack, defense, and weaknesses for each trio and the complete team
    -> Reflection checkpoint:
        -> if decision=refine:
            -> Agent E selects 1 replacement or adjustment to correct the priority gap
            -> Agent A collects data for new candidates
            -> Agent B updates the proposal
            -> Agent C revalidates
            -> Agent D reaudits
            -> Agent F revisits affected set details
        -> if decision=ask_user or decision=stop_with_pending:
            -> stop with the relevant question or pending issue
        -> if decision=accept:
            -> Agent F populates final moves, EVs, nature, item, and usage suggestions
    -> Set detail reflection checkpoint:
        -> if decision=refine:
            -> Agent A collects one focused missing move, item, Pokemon, or type data need
            -> Agent F updates affected set details
        -> if decision=ask_user or decision=stop_with_pending:
            -> stop with the relevant question or pending issue
        -> if decision=accept:
            -> continue
    -> Complete-member validation gate:
        -> verify each final Pokemon has identity, ownership, role, trio, reason, four moves with reasons, EVs, nature, item, usage suggestion, notes, and AI gap coverage when applicable
        -> if a required field can be filled by one focused tool call:
            -> Agent A collects the missing data
            -> Agent F updates affected set details
        -> if a required field cannot be validated or justified:
            -> stop_with_pending
        -> if every member is complete:
            -> continue
    -> Final reflection checkpoint:
        -> confirm decision=accept or stop with declared pending issues
        -> finalize response
```

## Completion Conditions

The flow should finish only when:

- the team has exactly six Pokemon;
- the team is separated into two trios of three Pokemon;
- two aces are identified, each with a different strategy;
- the trios are complementary while preserving distinct identities;
- all user Pokemon were preserved or recorded as pending;
- each AI-selected Pokemon has a role, reason, and covered gap;
- Agent F populated complete detailed sets for each final Pokemon;
- each populated set has four moves with reasons, EVs with named point values, nature, item, and usage suggestion;
- no final Pokemon is missing a required complete-member field;
- relevant risks and uncertainties are declared;
- the final format follows `docs/agentic-team-pattern.md`.

## Blocking Conditions

The flow should stop and ask for confirmation when:

- a user-provided Pokemon cannot be identified;
- user restrictions make it impossible to complete six valid members;
- user restrictions prevent choosing two aces or two distinct strategies;
- the PokeAPI-compatible source is unavailable and real data is required;
- preserving fixed choices conflicts with an explicit user restriction.
