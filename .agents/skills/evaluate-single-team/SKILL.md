---
name: evaluate-single-team
description: Use when any AI agent needs to evaluate one six-Pokemon single battle team, validate two-trio structure, completeness, strategy cohesion, balance risks, and produce unstructured text feedback blocks so the creation/orchestration agent can redo its analysis using only currently available Pokemon MCP tools for factual checks.
argument-hint: "<team-json-or-team-text> | <primary-strategy> | [complementary-strategy] | [constraints]"
---

# Evaluate Single Team

## Description, Usage, And Examples

Evaluate one proposed single battle team and return unstructured feedback blocks
for the creation/orchestration agent. This skill acts as an evaluator sub-agent:
it does not build a replacement team, does not create full Pokemon sets, and does
not silently fix members. It points out concrete improvement areas so the
creation agent can redo its analysis, revisit assumptions, and revise Pokemon,
roles, moves, items, trios, or strategy assignments.

Usage:

```text
evaluate-single-team <team-json-or-team-text> | <primary-strategy> | [complementary-strategy] | [constraints]
```

Examples:

```text
evaluate-single-team team.json | rain offense | bulky balance | champions_only=true
evaluate-single-team team text | dragon dance sweep | hazard control | no duplicate items
evaluate-single-team draft team | special wallbreak | speed control | preserve locked user Pokemon
```

## Inputs

Receive and preserve:

- `team`: one proposed team package or unstructured team draft.
- `primary_strategy`: declared strategy for the primary trio.
- `complementary_strategy`: optional declared strategy for the complementary trio.
- `constraints`: optional rules such as Champions-only, no duplicate items,
  preserve locked Pokemon, required ace, banned Pokemon, or matchup priorities.

Each Pokemon should include, when available: `name`, `source`, `locked`, `role`,
`trio`, `ability`, `item`, `nature`, `types`, `moves`, `added_points`, metadata,
validation, and pending issues. If fields are missing, treat that as feedback for
revision instead of filling the gap.

## Data Rule

Use only the currently available Pokemon MCP tools listed below to verify Pokemon
facts. This is a closed allowlist: do not use any other MCP tool, CLI, Python
module, repository source file, test fixture, memory, web search, direct PokeAPI
call, local source-code assumption, or external knowledge to fill Pokemon facts.

Allowed factual MCP tools:

- `rank_pokemon`: verify candidate stat/type profile when the team data is
  insufficient and the requested check can be expressed through ranking filters.
- `rank_pokemon_moveset`: verify move availability and move details for a focused
  Pokemon when move completeness or role fit is disputed.
- `list_items`: verify item facts when item presence, duplication, or fit matters.
- `validate_champions_legality`: verify Pokemon, ability, move, or item facts
  when Champions scope, legality, or completeness matters.
- `get_type_relations`: verify type weaknesses, resistances, immunities, and
  matchup claims for focused team or trio risks.

If one of these tools is not available in the running agent environment, treat
that fact as unavailable. Do not replace it with another tool or access path. Add
a feedback note with code `tool_unavailable` when the missing tool blocks a fact
check.

## Evaluation Steps

1. Parse the submitted team as far as possible and preserve all `source=user` and
   `locked=true` Pokemon as fixed members.
2. Check structure:
   - exactly six Pokemon;
   - exactly two trios of three Pokemon;
   - one primary trio and one complementary trio;
   - at least one ace per trio;
   - primary and complementary strategies are distinct.
3. Check member completeness against the package expected from `create-pokemon`:
   - `name`, `ability`, `item`, `nature`, `types`, `moves`, and `added_points`;
   - exactly four moves per Pokemon;
   - every move has `name`, `power`, `pp`, `description`, `priority`, `type`, and
     `damage_class`;
   - `added_points` includes `hp`, `attack`, `defense`, `special_attack`,
     `special_defense`, and `speed`.
4. Check team rules:
   - no duplicate Pokemon unless the caller explicitly allows them;
   - no duplicate items when `constraints` forbid item repetition;
   - user locked Pokemon are preserved;
   - no blocking pending issue is hidden inside a member package.
5. Audit strategy cohesion:
   - primary trio supports the primary ace and primary strategy;
   - complementary trio has its own real plan, not only support for the primary;
   - roles are not excessively redundant;
   - physical/special pressure, speed, durability, and support are reasonably
     distributed for the declared strategies.
6. Audit team versatility:
   - identify repeated Pokemon types that make the team narrower or create shared
     weaknesses;
   - identify repeated roles/functions, such as too many sweepers, walls, pivots,
     setup users, hazard setters, or support-only members;
   - identify repeated key-stat focus, such as too much investment or strategic
     dependency on only speed, attack, special-attack, bulk, or one defensive stat;
   - identify repeated moves or repeated move categories that reduce coverage,
     utility, or matchup flexibility;
   - distinguish intentional redundancy from harmful redundancy. Intentional
     redundancy must clearly support the declared strategy; otherwise ask the
     creation agent to diversify.
7. Audit balance and coverage:
   - use provided types first;
   - call `get_type_relations` only for focused weaknesses or matchup claims that
     materially affect the feedback;
   - distinguish acceptable risk from blocking imbalance.
8. Use focused MCP validation only when it can materially improve the feedback.
   Prefer asking the orchestrator to redo the draft when many facts are missing.
9. Produce concise text feedback blocks with concrete revision demands for the
   creation/orchestration agent.

## Required Feedback Output

Always return unstructured text blocks. Do not return JSON, tables, or a rigid
schema. The feedback should be readable by another AI agent and should emphasize
what must be reconsidered, why it matters, and what kind of revision is expected.

Use these block types as natural-language headings when useful, but do not force
empty sections:

```text
Overall verdict
State whether the team should be accepted, revised, or blocked. Explain the main
reason in one or two sentences.

Structural problems
Call out issues with team size, trio split, aces, locked Pokemon preservation,
duplicates, duplicate items when forbidden, or missing required member fields.

Strategic problems
Explain where the primary plan, complementary plan, ace roles, role spread, or
trio distinction does not hold together.

Balance problems
Explain type, speed, physical/special, defensive, item, utility, or matchup
risks. Use MCP-backed evidence when making factual claims.

Versatility problems
Point out repeated types, repeated functions, repeated key-stat focus, repeated
setup patterns, repeated utility roles, or repeated moves that make the team too
predictable. Explain which repetitions should be diversified and which are
acceptable because they directly support the declared strategy.

Data and validation gaps
List missing or unavailable facts, tool limitations, unresolved member pending
issues, or `tool_unavailable` blockers. Do not fill missing facts by assumption.

Revision demands for the creation agent
Write direct instructions for what the creation/orchestration agent should redo.
Examples: rerun create-pokemon for a specific member, ask list-pokemon for a
replacement with a specific role/type/stat profile, diversify repeated moves,
rebalance one trio, validate one item, or ask the user before changing a locked
Pokemon.

What to preserve
Mention team pieces that are working and should not be changed unless needed.
```

## Verdict Rules

Use an accept verdict only when:

- the team has exactly six complete Pokemon;
- the team has two valid trios of three;
- each trio has a distinct ace and strategy;
- locked user Pokemon are preserved;
- no blocking member pending issue exists;
- no critical or major finding requires revision;
- factual claims used in the evaluation are supported by submitted data or the
  allowlisted MCP tools;
- type, role, key-stat, and move repetition is either low enough for versatility
  or explicitly justified by the declared strategy.

Use a revise verdict when:

- the team is structurally close but one or more actionable improvements are
  needed;
- the creation/orchestration agent can fix the issue by calling `list-pokemon`,
  `create-pokemon`, or a focused MCP validation step;
- user confirmation is not strictly required before a revision can be attempted.

Use a blocked verdict when:

- the team cannot be evaluated because required data is missing and unavailable;
- constraints conflict, such as locked duplicate Pokemon with no permission to
  replace them;
- a required MCP tool is unavailable and the missing fact blocks the decision;
- user confirmation is required before the creation/orchestration agent can
  proceed.

## Revision Feedback Rules

- Make revision feedback concrete and actionable for the creation/orchestration
  agent.
- Preserve locked user Pokemon unless the feedback explicitly says to request
  user confirmation before replacement.
- Tell the agent to use `list-pokemon` for candidate-search revisions,
  especially when repeated types or roles should be diversified.
- Tell the agent to use `create-pokemon` for set-detail fixes, especially when
  repeated moves, repeated key-stat focus, or narrow coverage should be revised.
- Tell the orchestrator to handle whole-team structural changes.
- Clearly label blockers that prevent acceptance.
- Do not propose a replacement Pokemon by name unless that name came from the
  submitted team or an allowlisted MCP tool call during evaluation.

## Versatility Review Rules

- Treat repeated types as a revision concern when they create stacked weaknesses,
  leave a trio with narrow defensive switching, or make both trios answer the same
  matchups in the same way.
- Treat repeated functions as a revision concern when multiple Pokemon compete for
  the same job without adding a different matchup, tempo, or win condition.
- Treat repeated key-stat focus as a revision concern when too many members rely
  on the same attribute, such as speed-only pressure, attack-only damage,
  special-attack-only damage, or one-sided bulk. Ask for mixed pressure, extra
  utility, or defensive variety when the strategy permits it.
- Treat repeated moves as a revision concern when the overlap reduces coverage,
  status diversity, hazard control, priority, recovery, pivoting, or setup
  options. Do not claim a move is available or unavailable unless submitted data
  or `rank_pokemon_moveset` supports that fact.
- Accept some redundancy only when it is strategy-critical, such as deliberate
  weather abuse, layered speed control, repeated recovery on a stall plan, or
  backup coverage for a known matchup. Even then, ask whether the redundancy can
  be diversified without weakening the core plan.
- Prefer feedback that increases versatility: request a different type, a
  different role, a different damage class, a different utility move, a different
  key stat, or a complementary trio identity.

## Limits

- Do not build full teams or replacement teams.
- Do not create complete Pokemon packages; request `create-pokemon` revisions
  instead.
- Do not list new candidate pools directly unless the data came from
  `rank_pokemon`; prefer telling the agent to use `list-pokemon`.
- Do not replace the allowlisted MCP tools with any other MCP tool, memory,
  internet, external files, direct PokeAPI calls, CLIs, Python imports, tests,
  fixture files, or source-code assumptions.
- Do not call `build_pokemon_team` or `search_champions_strategy`.
- Do not claim the team is ready when any blocking pending issue exists.
