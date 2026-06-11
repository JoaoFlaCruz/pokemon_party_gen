## MODIFIED Requirements

### Requirement: Data-backed validation
The system SHALL validate Pokemon names, identifiers, Champions library membership, and candidate details through existing PokeAPI-compatible data access or injected fakes in tests.

#### Scenario: Unknown user-selected Pokemon
- **WHEN** a user-selected Pokemon cannot be found through the configured data source
- **THEN** the system records the unresolved entry in `pending` and does not invent stats, types, moves, abilities, item details, or Champions membership for it.

#### Scenario: Candidate data source unavailable
- **WHEN** required Pokemon data or Champions Pokédex membership cannot be fetched from the configured data source
- **THEN** the system returns a pending issue describing the data failure instead of fabricating a team member.

#### Scenario: User-selected Pokemon outside Champions library
- **WHEN** a validated user-selected Pokemon is not present in the Champions Pokédex
- **THEN** the system preserves it as a locked user-selected member and records the out-of-library status in `pending`.

### Requirement: Six-member team output
The system SHALL return a structured team response containing exactly six team slots when enough validated Pokemon can satisfy the request, with AI-selected slots limited to the Pokemon Champions library.

#### Scenario: Team can be completed
- **WHEN** the user provides fewer than six validated Pokemon and enough validated Champions candidates are available
- **THEN** the system fills the remaining slots with AI-selected Pokemon marked with `source=ai`, `locked=false`, and Champions library membership.

#### Scenario: Team cannot be completed
- **WHEN** fewer than six validated Pokemon can be selected because of data failures, Champions library scope, or conflicting constraints
- **THEN** the system returns the partial validated result and records the completion problem in `pending`.

### Requirement: Selection explanations
The system SHALL include objective role, reason, gap-coverage, and Champions library scope fields for each AI-selected Pokemon.

#### Scenario: AI-selected member explanation
- **WHEN** the system adds an AI-selected Pokemon to the team
- **THEN** that member includes `role`, `reason`, `replaces_gap`, and a field indicating it was selected from the Pokemon Champions library.

#### Scenario: User-selected member explanation
- **WHEN** the system includes a user-selected Pokemon in the team
- **THEN** that member includes `role` when inferable, a reason indicating it was selected by the user, and Champions library membership status when known.

### Requirement: Analysis and pending output
The system SHALL return team-level analysis, Champions library scope, and pending issues in a predictable JSON-serializable structure.

#### Scenario: Completed team analysis
- **WHEN** the system completes a six-Pokemon team
- **THEN** the response includes `analysis.strengths`, `analysis.trio_differences`, `analysis.trio_complementarity`, `analysis.risks`, `analysis.selection_criteria`, and metadata indicating AI candidates were constrained to the Pokemon Champions library.

#### Scenario: Pending issue exists
- **WHEN** validation, data availability, Champions library scope, or user constraints prevent a confident decision
- **THEN** the response includes a `pending` entry with the affected input or decision and a human-readable reason.
