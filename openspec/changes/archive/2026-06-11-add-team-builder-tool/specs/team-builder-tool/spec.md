## ADDED Requirements

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
