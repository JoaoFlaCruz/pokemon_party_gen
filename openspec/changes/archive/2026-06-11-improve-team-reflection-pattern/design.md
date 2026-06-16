## Context

The current team-builder capability documents a deterministic MCP tool and an agentic A-E workflow for creating six-Pokemon teams. The workflow already includes validation, balance audit, candidate selection, and a 1-to-5-call operating model, but its reflection step does not define when reflection happens or how an agent decides whether to refine or stop.

This change improves that workflow contract through documentation and spec updates. It does not require a new tool, new schema fields, or changes to the deterministic `build_pokemon_team` orchestration.

## Goals / Non-Goals

**Goals:**

- Define reflection checkpoints in the team-building workflow.
- Standardize reflection decisions as `accept`, `refine`, `ask_user`, or `stop_with_pending`.
- Tie reflection to existing constraints: user-selected Pokemon preservation, six-member teams, two distinct trios, two distinct aces, objective AI-selected reasons, pending issues, and the 1-to-5-call model.
- Add loop-control guidance so agents avoid unnecessary calls and repeated low-value refinement.

**Non-Goals:**

- Add a new MCP tool or change the `build_pokemon_team` input/output schema.
- Generate competitive movesets, held items, or matchup audits automatically beyond existing tool capabilities.
- Replace the existing A-E agent responsibilities.

## Decisions

1. Document reflection as workflow behavior, not runtime state.

   Rationale: The reflection pattern guides AI orchestration around existing tools. Adding structured runtime fields would expand the MCP contract without a current implementation need.

   Alternative considered: Add `reflection` to `structuredContent.data`. This was rejected for now because it would require code and tests for a presentation concern that can be enforced through the agentic workflow documentation.

2. Use a small fixed decision vocabulary.

   Rationale: `accept`, `refine`, `ask_user`, and `stop_with_pending` cover the meaningful outcomes after validation and audit while keeping agent behavior easy to inspect.

   Alternative considered: Free-form reflection notes only. This was rejected because they are harder to test against and do not reliably stop unnecessary calls.

3. Place loop control inside the existing 1-to-5-call model.

   Rationale: Reflection should decide whether another call is useful. It should not encourage always using all five calls.

   Alternative considered: Define reflection as a mandatory fifth call. This was rejected because simple team requests should remain satisfiable with one call.

## Risks / Trade-offs

- [Risk] Agents may treat reflection as verbose user-facing analysis. -> Mitigation: Document reflection as a concise internal decision checkpoint and only expose relevant risks, pending issues, and final rationale.
- [Risk] Reflection could encourage over-refinement. -> Mitigation: Require a concrete expected benefit before additional calls and stop when data, constraints, or call budget prevent meaningful improvement.
- [Risk] Documentation-only changes may not affect every client. -> Mitigation: Update the OpenSpec contract and both team-flow docs so future implementation and agent behavior share the same source of truth.
