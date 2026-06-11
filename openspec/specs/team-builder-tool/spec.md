## Purpose

Define the MCP contract for building a complete six-Pokemon team from user-selected Pokemon, optional strategies, and validated PokeAPI-compatible data.

## Requirements

### Requirement: Team builder tool schema
The system SHALL expose a `build_pokemon_team` MCP tool that accepts user-selected Pokemon and optional team-building constraints.

#### Scenario: Tool is listed
- **WHEN** an MCP client calls `tools/list`
- **THEN** the response includes a `build_pokemon_team` tool with an input schema.

#### Scenario: Minimal valid request
- **WHEN** the tool is called with no user-selected Pokemon and no optional constraints
- **THEN** the system accepts the request and attempts to build a six-Pokemon team from validated candidates.

#### Scenario: Invalid selected Pokemon input
- **WHEN** the tool is called with `pokemon` that is not an array of strings or integers
- **THEN** the system returns a validation error.

### Requirement: User-selected Pokemon preservation
The system SHALL preserve validated user-selected Pokemon as fixed team members in the order provided by the user.

#### Scenario: User choices are locked
- **WHEN** the user provides valid Pokemon identifiers
- **THEN** each validated selected Pokemon appears in the output with `source=user` and `locked=true`.

#### Scenario: Duplicate user choices
- **WHEN** the user provides the same Pokemon more than once
- **THEN** the system keeps the first occurrence, omits later duplicates from team slots, and records the duplicate handling in the output.

#### Scenario: More than six user choices
- **WHEN** the user provides more than six Pokemon
- **THEN** the system uses only the first six unique entries and records that the limit was applied.

### Requirement: Data-backed validation
The system SHALL validate Pokemon names, identifiers, and candidate details through existing PokeAPI-compatible data access or injected fakes in tests.

#### Scenario: Unknown user-selected Pokemon
- **WHEN** a user-selected Pokemon cannot be found through the configured data source
- **THEN** the system records the unresolved entry in `pending` and does not invent stats, types, moves, abilities, or item details for it.

#### Scenario: Candidate data source unavailable
- **WHEN** required Pokemon data cannot be fetched from the configured data source
- **THEN** the system returns a pending issue describing the data failure instead of fabricating a team member.

### Requirement: Six-member team output
The system SHALL return a structured team response containing exactly six team slots when enough validated Pokemon can satisfy the request.

#### Scenario: Team can be completed
- **WHEN** the user provides fewer than six validated Pokemon and enough validated candidates are available
- **THEN** the system fills the remaining slots with AI-selected Pokemon marked with `source=ai` and `locked=false`.

#### Scenario: Team cannot be completed
- **WHEN** fewer than six validated Pokemon can be selected because of data failures or conflicting constraints
- **THEN** the system returns the partial validated result and records the completion problem in `pending`.

### Requirement: Trio structure
The system SHALL structure completed teams into `primary` and `complementary` trios of three Pokemon each, with distinct ace Pokemon and strategy labels.

#### Scenario: Completed team trios
- **WHEN** the system returns a completed six-Pokemon team
- **THEN** the `team_structure` identifies primary and complementary trio strategies and each team member has a `trio` value of `primary` or `complementary`.

#### Scenario: User provides one ace
- **WHEN** the user identifies one selected Pokemon as an ace or provides only one obvious ace candidate
- **THEN** the system keeps that Pokemon in the primary trio and selects or identifies a different complementary ace when enough validated data is available.

#### Scenario: User provides two aces
- **WHEN** the user identifies two selected Pokemon as aces
- **THEN** the system places them as separate trio aces unless validation or constraints make that impossible, in which case it records a pending issue.

### Requirement: Selection explanations
The system SHALL include objective role, reason, and gap-coverage fields for each AI-selected Pokemon.

#### Scenario: AI-selected member explanation
- **WHEN** the system adds an AI-selected Pokemon to the team
- **THEN** that member includes `role`, `reason`, and `replaces_gap` values.

#### Scenario: User-selected member explanation
- **WHEN** the system includes a user-selected Pokemon in the team
- **THEN** that member includes `role` when inferable and a reason indicating it was selected by the user.

### Requirement: Analysis and pending output
The system SHALL return team-level analysis and pending issues in a predictable JSON-serializable structure.

#### Scenario: Completed team analysis
- **WHEN** the system completes a six-Pokemon team
- **THEN** the response includes `analysis.strengths`, `analysis.trio_differences`, `analysis.trio_complementarity`, `analysis.risks`, and `analysis.selection_criteria`.

#### Scenario: Pending issue exists
- **WHEN** validation, data availability, or user constraints prevent a confident decision
- **THEN** the response includes a `pending` entry with the affected input or decision and a human-readable reason.

### Requirement: MCP response format
The system SHALL return MCP tool results with both presentation text and structured content.

#### Scenario: Tool call response
- **WHEN** an MCP client calls `build_pokemon_team`
- **THEN** the MCP server returns `content` with a text presentation and `structuredContent` containing `tool_name`, `input`, `data`, and `presentation`.

### Requirement: English team-building documentation
The system SHALL document the team-builder tool and agentic team-building flow in English while preserving exact tool names, JSON keys, command examples, and behavioral contracts.

#### Scenario: Documentation is translated
- **WHEN** a maintainer reads the project documentation for architecture, team-building rules, or agentic team flow
- **THEN** the prose is available in English and preserves the existing technical meaning.

#### Scenario: Technical identifiers are preserved
- **WHEN** documentation references tool names, response fields, role values, commands, file paths, or JSON examples
- **THEN** those identifiers remain exact and are not translated into prose-only equivalents.

#### Scenario: Documentation file names are translated
- **WHEN** Portuguese Markdown documentation files are translated to English
- **THEN** their file names are also renamed to English equivalents and repository references are updated to the new paths.

### Requirement: One-to-five-call agentic flow
The system SHALL document a 1-to-5-call decision guide for team-building agents using `build_pokemon_team` and supporting MCP tools.

#### Scenario: Single-call path
- **WHEN** a user asks for a basic complete team without detailed validation
- **THEN** the documentation identifies one `build_pokemon_team` call as the minimum sufficient path.

#### Scenario: Deeper validation path
- **WHEN** a user asks for candidate comparison, moveset confidence, type auditing, itemization, or correction of a known weakness
- **THEN** the documentation explains which additional calls should be used up to a maximum recommended sequence of five calls.

#### Scenario: Avoid unnecessary calls
- **WHEN** a simple request can be satisfied with fewer calls
- **THEN** the documentation directs agents to stop at the lowest call count that satisfies the request and declared validation needs.

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
