## ADDED Requirements

### Requirement: Reflection checkpoints
The system SHALL document explicit reflection checkpoints for agentic Pokemon team creation before finalizing a recommendation.

#### Scenario: Initial team reflection
- **WHEN** an agent receives an initial `build_pokemon_team` result
- **THEN** the documented workflow requires a reflection checkpoint that checks completion, preserved user choices, trio structure, ace distinction, pending issues, and whether additional calls are justified.

#### Scenario: Validation reflection
- **WHEN** strategic validation reports `valid`, `needs_refinement`, or `blocked_by_data`
- **THEN** the documented workflow requires a reflection checkpoint that chooses whether to proceed, refine the candidate set, ask the user, or stop with declared pending issues.

#### Scenario: Audit reflection
- **WHEN** balance auditing identifies weaknesses, redundancies, or unresolved gaps
- **THEN** the documented workflow requires a reflection checkpoint that distinguishes acceptable risk from a blocker requiring one focused correction.

#### Scenario: Final response reflection
- **WHEN** an agent is ready to present the team
- **THEN** the documented workflow requires a final reflection checkpoint that confirms the response satisfies the user request and declares relevant risks or unresolved data.

### Requirement: Reflection decisions
The system SHALL document a fixed reflection decision vocabulary for agentic Pokemon team creation.

#### Scenario: Accept decision
- **WHEN** the team satisfies the request, preserves user choices, has six validated members when enough data is available, and has no blocker that another call is expected to improve
- **THEN** the reflection decision is `accept`.

#### Scenario: Refine decision
- **WHEN** a specific team gap can be improved by one additional candidate, moveset, type, item, or correction call within the documented call model
- **THEN** the reflection decision is `refine` and the workflow identifies the next call and expected improvement.

#### Scenario: Ask user decision
- **WHEN** user constraints are ambiguous, conflict with fixed Pokemon, or require a preference that cannot be inferred from validated data
- **THEN** the reflection decision is `ask_user` and the workflow stops until the user resolves the ambiguity.

#### Scenario: Stop with pending decision
- **WHEN** data is unavailable, constraints prevent a complete confident team, or additional calls would not change the recommendation
- **THEN** the reflection decision is `stop_with_pending` and the workflow reports the unresolved issue in the final response.

### Requirement: Reflection loop control
The system SHALL document loop-control rules that keep Pokemon team reflection bounded and aligned with the 1-to-5-call operating model.

#### Scenario: Lowest sufficient call count
- **WHEN** the user request can be satisfied with fewer than five calls
- **THEN** the documented workflow directs agents to stop at the lowest call count that satisfies the request and validation needs.

#### Scenario: Focused refinement
- **WHEN** reflection chooses `refine`
- **THEN** the documented workflow limits the next step to the highest-priority gap and requires a concrete reason the additional call can improve the recommendation.

#### Scenario: Preserve locked Pokemon during refinement
- **WHEN** reflection identifies a weakness caused by a user-selected Pokemon
- **THEN** the documented workflow requires preserving that Pokemon as locked and correcting around it unless the user explicitly confirms a replacement.

#### Scenario: Avoid repeated low-value refinement
- **WHEN** a refinement would repeat the same kind of call without new information or would exceed the documented call model
- **THEN** the documented workflow requires `accept`, `ask_user`, or `stop_with_pending` instead of continuing the loop.
