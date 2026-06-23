---
name: create-pokemon
description: Use when any AI agent needs to create one validated Pokemon JSON package for a larger team/list from a Pokemon name, strategy or role, optional item, and key stat, using only the currently available Pokemon MCP tools for factual data.
argument-hint: "<pokemon-name> | <strategy-or-role> | [item] | <key-stat>"
---

# Create Pokemon

## Description, Usage, And Examples

Create one structured Pokemon package for a main team/list. This skill acts as a
sub-agent: it does not build a full team, does not choose the other members, and
does not replace user choices. It returns a single formatted JSON package with
validated Pokemon facts, selected moves, ability, item, nature, types, and added
stat-point distribution.

Usage:

```text
create-pokemon <pokemon-name> | <strategy-or-role> | [item] | <key-stat>
```

Examples:

```text
create-pokemon Garchomp | physical sweeper | choice-scarf | speed
create-pokemon Rotom-Wash | defensive pivot | leftovers | hp
create-pokemon Volcarona | special setup win condition | | special-attack
```

## Inputs

Receive and preserve:

- `pokemon_name`: Pokemon name or queryable identifier.
- `strategy_or_role`: expected strategy, function, or role.
- `item`: requested held item, when present.
- `key_stat`: key attribute used to guide moves, stat points, nature, and usage.

If `pokemon_name`, `strategy_or_role`, or `key_stat` is missing, ask for it
before running the workflow. If only `item` is missing, continue without a fixed
item and choose one only when MCP item data supports the recommendation; otherwise
return the item as `null` and record a blocking or non-blocking pending issue.

## Data Rule

Use only the currently available Pokemon MCP tools listed below to obtain Pokemon
facts. This is a closed allowlist: do not use any other MCP tool, CLI, Python
module, repository source file, test fixture, memory, web search, direct PokeAPI
call, local source-code assumption, or external knowledge to fill Pokemon facts.

Allowed factual MCP tools:

- `rank_pokemon`: collect structured Pokemon identity, type/stat profile, or
  ranked candidates when the tool supports the needed query.
- `rank_pokemon_moveset`: mandatory move tool; use it to evaluate moves for the
  requested Pokemon.
- `list_items`: mandatory when an item is provided or when the final package
  recommends an item.
- `validate_champions_legality`: validate Pokemon, ability, move, or item facts
  in Champions scope when the request needs Champions legality, legal validation,
  or completeness checks.
- `get_type_relations`: query matchups when the strategy depends on coverage,
  weakness, resistance, or immunity.

If one of these tools is not available in the running agent environment, treat
that fact as unavailable. Do not replace it with another tool or access path.
Return the unresolved field as `null` when allowed, set `validation.complete` to
`false`, and add a `pending` entry with code `tool_unavailable`.

If MCP data does not provide a required fact, do not invent it. Return `null` for
the unresolved field when the JSON schema allows it, set `validation.complete` to
`false`, and add a `pending` entry with the useful diagnostic fields returned by
the tool. Common diagnostic codes include `pokemon_not_found`,
`outside_champions_scope`, `incomplete_data`, `source_unavailable`,
`unsupported_validation`, and `no_eligible_candidates`.

## Steps

1. Parse the input into `pokemon_name`, `strategy_or_role`, `item`, and
   `key_stat`.
2. Collect Pokemon data with MCP tools:
   - use `validate_champions_legality` when Champions scope, legal validation, or
     completeness is relevant;
   - use `rank_pokemon` when stat profile, type identity, or key-stat fit must be
     confirmed.
3. Call `rank_pokemon_moveset` for the requested Pokemon. Select exactly four
   moves only from MCP-returned or MCP-validated data.
4. For every selected move, populate:
   - `name`;
   - `power`;
   - `pp`;
   - `description`;
   - `priority`, as boolean `true` when the MCP numeric priority is greater than
     zero, otherwise `false`;
   - `type`;
   - `damage_class`, using only `physical`, `special`, or `status`;
   - `reason`.
5. If a move description is not available from MCP data, keep the move only when
   its required battle fields are validated, set `description` to `null`, and add
   a pending issue for the missing description. Do not write a description from
   memory.
6. If `item` was provided, validate it with `list_items` or
   `validate_champions_legality`. If no item was provided, call `list_items` only
   when the final recommendation needs an item and the choice can be supported by
   returned MCP data.
7. Choose or confirm `ability` only from MCP-returned or MCP-validated data. If
   the available MCP tools do not provide a validated ability, set `ability` to
   `null` and record the pending issue.
8. Define `nature` and `added_points` as strategic recommendations tied to
   validated facts: key stat, base stats, move damage classes, item, and role.
   The `added_points` object must include all six Pokemon attributes even when a
   stat receives zero added points.
9. Run the completeness gate. A package can set `validation.complete=true` only
   when all required output fields are populated with MCP facts or justified
   strategic recommendations and `pending` has no blocking issue.

## Required JSON Output

Always return a formatted JSON object. Do not return prose instead of JSON. The
top-level package must use this shape:

```json
{
  "name": "pokemon-name",
  "ability": "ability-name-or-null",
  "item": "item-name-or-null",
  "nature": "nature-name",
  "types": ["type-a", "type-b"],
  "moves": [
    {
      "name": "move-a",
      "power": 90,
      "pp": 10,
      "description": "MCP-provided move description or null",
      "priority": false,
      "type": "move-type",
      "damage_class": "physical",
      "reason": "why this move fits the role"
    },
    {
      "name": "move-b",
      "power": null,
      "pp": 20,
      "description": "MCP-provided move description or null",
      "priority": true,
      "type": "move-type",
      "damage_class": "status",
      "reason": "why this move fits the role"
    },
    {
      "name": "move-c",
      "power": 80,
      "pp": 15,
      "description": "MCP-provided move description or null",
      "priority": false,
      "type": "move-type",
      "damage_class": "special",
      "reason": "why this move fits the role"
    },
    {
      "name": "move-d",
      "power": 100,
      "pp": 5,
      "description": "MCP-provided move description or null",
      "priority": false,
      "type": "move-type",
      "damage_class": "physical",
      "reason": "why this move fits the role"
    }
  ],
  "added_points": {
    "hp": 0,
    "attack": 0,
    "defense": 0,
    "special_attack": 0,
    "special_defense": 0,
    "speed": 0
  },
  "metadata": {
    "source": "ai",
    "locked": false,
    "strategy_or_role": "strategy or role",
    "key_stat": "key-stat",
    "usage_suggestion": "how to use the Pokemon in its assigned role",
    "notes": [],
    "data_sources": [
      "rank_pokemon",
      "rank_pokemon_moveset",
      "list_items"
    ]
  },
  "validation": {
    "complete": false,
    "blocking_pending": true
  },
  "pending": [
    {
      "code": "incomplete_data",
      "message": "Missing MCP-validated ability.",
      "entity": "pokemon-name",
      "missing_fields": ["ability"],
      "blocking": true
    }
  ]
}
```

## Completion Rules

- `moves` must contain exactly four entries.
- Each move must include `name`, `power`, `pp`, `description`, `priority`,
  `type`, `damage_class`, and `reason`.
- `priority` must be a boolean, not the raw numeric priority value.
- `damage_class` must be `physical`, `special`, or `status`.
- `added_points` must include all six attributes: `hp`, `attack`, `defense`,
  `special_attack`, `special_defense`, and `speed`.
- Use `null` only for fields whose facts are unavailable from MCP data, then add
  a matching `pending` item.
- Do not set `validation.complete=true` when any required field is `null`, when
  fewer or more than four moves are present, or when any blocking pending issue
  exists.

## Limits

- Do not build full teams; return only one Pokemon package for the main list.
- Do not replace the allowlisted MCP tools with any other MCP tool, memory,
  internet, external files, direct PokeAPI calls, CLIs, Python imports, tests,
  fixture files, or source-code assumptions.
- Do not call `build_pokemon_team` or `search_champions_strategy`.
- Do not accept fewer or more than four moves in a complete Pokemon package.
- Do not mark `validation.complete=true` when any mandatory data is unresolved.
