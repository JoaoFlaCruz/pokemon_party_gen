## Context

The active team-building path is an AI workflow that uses lower-level MCP tools for Pokemon, moves, items, and type data. `build_pokemon_team` is not an active MCP tool and must not be used as the owner of new team-output behavior.

Current docs define Agents A-E. Agent B can draft movesets, stats, and items when available, but this mixes base composition with detailed set population. The requested detailed output is better handled after the team strategy and membership stabilize, because moves, EVs, nature, and item depend on each Pokemon's final role inside a trio and on the complete team's strategy.

## Goals / Non-Goals

**Goals:**

- Add Agent F as a dedicated Set Populator in the active agentic workflow.
- Make Agent F responsible for populating per-Pokemon moves, EVs, nature, item, and usage suggestion according to role, trio strategy, and validated data.
- Update `.codex/skills/create-single-team/SKILL.md` so generated teams use Agent F and return the detailed member structure.
- Keep `build_pokemon_team` inactive and outside this new behavior.

**Non-Goals:**

- Reintroduce or replace `build_pokemon_team`.
- Add a new MCP tool for full team construction.
- Change lower-level MCP schemas for ranking, moveset ranking, type relations, item listing, or banned Pokemon.
- Require unsupported competitive claims when the available data cannot justify a set detail.

## Decisions

1. Create a new `agentic-team-assembly` capability instead of modifying `team-builder-tool`.

   Rationale: the active behavior is now agent orchestration, not a public MCP team-builder tool. A separate capability names the current owner clearly and avoids adding new requirements to a retired tool surface.

   Alternative considered: keep extending `team-builder-tool` because it contains historical team requirements. That preserves continuity but keeps future changes tied to a misleading capability name.

2. Place Agent F after Agent C and Agent D validate a stable draft, and rerun it after member or role changes.

   Rationale: set details depend on finalized roles, trio identity, team gaps, and risk audit. Running Agent F too early creates churn when Agent E later replaces candidates.

   Alternative considered: make Agent B continue to populate moves, EVs, nature, and items during initial drafting. That keeps fewer agents but overloads Agent B and makes final set consistency harder to validate.

3. Let Agent F request more data through Agent A rather than calling data tools directly in the documented workflow.

   Rationale: Agent A already owns data collection and traceability. This keeps the agent responsibilities clean: Agent F decides what set details are needed; Agent A gathers missing move, item, or relation data.

   Alternative considered: allow Agent F to query tools directly. That may be faster for simple cases but duplicates Agent A's responsibility and makes pending data harder to track.

## Risks / Trade-offs

- [Risk] Adding Agent F can lengthen the workflow for simple teams. -> Mitigation: Agent F should use the lowest sufficient validation depth and record pending details when additional calls would not improve confidence.
- [Risk] EVs and natures are strategic recommendations rather than direct PokeAPI facts. -> Mitigation: Agent F must tie them to role, stats, and strategy, and mark uncertainty in `pending` when confidence is insufficient.
- [Risk] The existing `team-builder-tool` spec still contains historical workflow requirements. -> Mitigation: introduce `agentic-team-assembly` as the active target and update docs/skills to point to the new capability during implementation.
