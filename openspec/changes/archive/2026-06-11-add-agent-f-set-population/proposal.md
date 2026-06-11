## Why

Team assembly no longer runs through the inactive `build_pokemon_team` MCP tool, so detailed per-Pokemon set population must belong to the active agentic workflow. A dedicated Agent F is needed to populate moves, EVs, nature, item, and usage guidance from the selected strategy after the team composition is validated.

## What Changes

- Introduce Agent F as the "Set Populator" responsible for filling each Pokemon's detailed battle set according to the selected role, trio strategy, and available validated data.
- Update the agentic workflow so Agent F runs after candidate selection and validation have produced a stable six-Pokemon draft, and runs again after refinements that change members or roles.
- Require Agent F to produce the per-Pokemon fields requested by the user: name, role/activity, reason, four moves with individual reasons, EV spread, nature, item, and usage suggestion.
- Require Agent F to record pending issues instead of inventing moves, EVs, natures, or items when data or confidence is insufficient.
- Update `.codex/skills/create-single-team/SKILL.md` so Codex-generated single-battle teams follow the six-agent flow and output the detailed per-Pokemon structure.
- Clarify that this change impacts the agentic team flow and skill instructions, not the inactive `build_pokemon_team` MCP tool.

## Capabilities

### New Capabilities

- `agentic-team-assembly`: Defines the active multi-agent workflow for assembling Pokemon teams without `build_pokemon_team`, including Agent F set population and required detailed member output.

### Modified Capabilities

None.

## Impact

- Affects `docs/agentic-team-flow.md` by adding Agent F and updating workflow, reflection, and completion criteria.
- Affects `docs/agentic-team-pattern.md` by requiring the detailed per-Pokemon response structure in the active agentic output format.
- Affects `.codex/skills/create-single-team/SKILL.md` by adding Agent F responsibilities and updating its response template.
- May affect `docs/architecture.md` to document Agent F in the architecture overview.
- Does not reactivate, replace, or change the inactive `build_pokemon_team` MCP tool.
- Does not add external dependencies or change lower-level MCP tool schemas.
