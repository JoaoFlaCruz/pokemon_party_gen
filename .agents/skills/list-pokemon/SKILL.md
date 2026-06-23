---
name: list-pokemon
description: Use when any AI agent needs to list possible Pokemon candidates for a specific strategy, role, type need, stat profile, or team gap, returning a simple JSON candidate list for an orchestration skill using only currently available Pokemon MCP tools.
argument-hint: "<strategy-or-role> | [types] | [key-stat] | [count] | [constraints]"
---

# List Pokemon

## Description, Usage, And Examples

List possible Pokemon candidates for a specific strategy or quality request. This
skill acts as a discovery sub-agent for an orchestration skill: it does not build
complete Pokemon sets, does not choose the final team, and does not fabricate
facts. It returns a simple formatted JSON package containing candidate Pokemon
that may fit the requested strategy.

Usage:

```text
list-pokemon <strategy-or-role> | [types] | [key-stat] | [count] | [constraints]
```

Examples:

```text
list-pokemon rain attacker | water,electric | special-attack | 8 | champions_only=true
list-pokemon defensive pivot | ground,flying | defense | 6 | needs fighting check
list-pokemon speed control | electric | speed | 10 | no duplicate with current team
```

## Inputs

Receive and preserve:

- `strategy_or_role`: requested strategy, function, role, or team gap.
- `types`: optional preferred type filters, up to two types when supported by the
  MCP tool.
- `key_stat`: optional priority stat such as `hp`, `attack`, `defense`,
  `special-attack`, `special-defense`, or `speed`.
- `count`: optional number of candidates to return.
- `constraints`: optional constraints such as Champions-only scope, current team
  exclusions, required coverage, speed preference, or physical/special leaning.

If `strategy_or_role` is missing, ask for it before running the workflow. If
other fields are missing, infer only the search shape, not Pokemon facts, and
record assumptions in `query.assumptions`.

## Data Rule

Use only the currently available Pokemon MCP tools listed below to obtain Pokemon
facts. This is a closed allowlist: do not use any other MCP tool, CLI, Python
module, repository source file, test fixture, memory, web search, direct PokeAPI
call, local source-code assumption, or external knowledge to fill Pokemon facts.

Allowed factual MCP tools:

- `rank_pokemon`: primary tool for candidate discovery by type, stat profile,
  speed mode, offensive stat, result count, and Champions scope.
- `rank_pokemon_moveset`: optional tool for checking whether a candidate's moves
  support the requested offensive role.
- `validate_champions_legality`: optional tool for checking Champions legality,
  Pokemon availability, ability, move, or item facts when legality/completeness is
  relevant.
- `get_type_relations`: optional tool for validating type matchup claims when the
  requested strategy depends on coverage, weakness, resistance, or immunity.
- `list_items`: optional only when the candidate list needs item-related
  filtering or item fit notes.

If one of these tools is not available in the running agent environment, treat
that fact as unavailable. Do not replace it with another tool or access path.
Return the best supported JSON result, set `validation.complete=false` when the
missing tool blocks the request, and add a `pending` entry with code
`tool_unavailable`.

If MCP data does not support a requested filter or fact, do not invent it. Return
the best MCP-supported candidate list, set `validation.complete=false` when the
unsupported fact is important, and add a `pending` entry.

## Steps

1. Parse the request into strategy, role, type filters, key stat, count, and
   constraints.
2. Convert the strategy into MCP-supported search criteria:
   - type filters for requested typing or coverage;
   - `priority_stat` for requested key stat;
   - `offense_stat` for physical or special leaning;
   - `speed_mode` for fast, slow, or speed-control requests;
   - `champions_only` according to the request, defaulting to the project tool
     default when unspecified.
3. Call `rank_pokemon` with the narrowest useful criteria and enough `head_size`
   to produce the requested count after exclusions.
4. Filter out Pokemon explicitly excluded by the orchestration context, such as
   current team duplicates or banned candidates, using only names from the MCP
   result and the caller's provided exclusions.
5. If role confidence depends on moves, call `rank_pokemon_moveset` for the most
   relevant top candidates only. Keep this focused; this skill lists candidates,
   while `create-pokemon` builds full sets.
6. If Champions legality or type matchup claims matter, use
   `validate_champions_legality` or `get_type_relations` for focused checks.
7. Return a formatted JSON object with candidate summaries, data sources,
   assumptions, and pending issues.

## Required JSON Output

Always return a formatted JSON object. Do not return prose instead of JSON. The
top-level package must use this shape:

```json
{
  "query": {
    "strategy_or_role": "rain attacker",
    "types": ["water"],
    "key_stat": "special-attack",
    "count": 6,
    "constraints": ["champions_only=true"],
    "assumptions": []
  },
  "candidates": [
    {
      "name": "pokemon-name",
      "types": ["type-a", "type-b"],
      "matched_strategy": "why this candidate may fit the requested strategy",
      "matched_qualities": [
        "special-attack profile",
        "water typing"
      ],
      "stats": {
        "hp": 0,
        "attack": 0,
        "defense": 0,
        "special_attack": 0,
        "special_defense": 0,
        "speed": 0
      },
      "source": "rank_pokemon",
      "confidence": "high",
      "notes": []
    }
  ],
  "metadata": {
    "candidate_count": 1,
    "data_sources": ["rank_pokemon"],
    "intended_consumer": "orchestration-skill"
  },
  "validation": {
    "complete": true,
    "blocking_pending": false
  },
  "pending": []
}
```

## Candidate Rules

- `candidates` may be empty only when MCP data returns no eligible candidates or
  a blocking source issue occurs.
- Each candidate must include `name`, `types`, `matched_strategy`,
  `matched_qualities`, `stats`, `source`, `confidence`, and `notes`.
- `stats` must include all six attributes using these keys: `hp`, `attack`,
  `defense`, `special_attack`, `special_defense`, and `speed`.
- Use confidence values `high`, `medium`, or `low`.
- Use `high` only when the candidate directly matches MCP-backed filters and any
  required focused validation passed.
- Use `medium` when the candidate matches the ranking/filter criteria but no
  additional move or legality validation was needed.
- Use `low` when the candidate is plausible from MCP ranking but a relevant
  role-specific fact is unresolved; add a matching `pending` item.

## Limits

- Do not build full Pokemon sets; call `create-pokemon` or return candidates to
  the orchestration skill for set creation.
- Do not build full teams or decide final team membership.
- Do not replace the allowlisted MCP tools with any other MCP tool, memory,
  internet, external files, direct PokeAPI calls, CLIs, Python imports, tests,
  fixture files, or source-code assumptions.
- Do not call `build_pokemon_team` or `search_champions_strategy`.
- Do not present a candidate quality as factual unless it is supported by MCP
  output or explicitly listed as an assumption/pending issue.
