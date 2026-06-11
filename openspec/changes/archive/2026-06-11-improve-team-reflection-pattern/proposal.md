## Why

The team-building workflow already defines a 1-to-5-call operating model, but the reflection step is underspecified. Agents need a clearer pattern for deciding whether to accept a team, refine it, ask the user, or stop with declared pending issues after validation and audit.

## What Changes

- Add explicit reflection checkpoints for Pokemon team creation after the initial team draft, after strategic validation, after balance audit, and before the final response.
- Define a small reflection decision vocabulary: `accept`, `refine`, `ask_user`, and `stop_with_pending`.
- Document reflection criteria that preserve user-selected Pokemon, enforce two distinct trios and aces, prioritize unresolved risks, and decide whether additional calls are justified.
- Add loop-control guidance so agents stop at the lowest sufficient call count and avoid repeated refinement when data or constraints cannot improve the team.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `team-builder-tool`: Add requirements for reflection checkpoints, reflection decisions, and reflection loop control in the documented agentic team-building workflow.

## Impact

- Affects `docs/agentic-team-flow.md` and `docs/agentic-team-pattern.md`.
- Updates the `team-builder-tool` OpenSpec contract.
- No new MCP tool, schema field, runtime dependency, or API breaking change is expected.
