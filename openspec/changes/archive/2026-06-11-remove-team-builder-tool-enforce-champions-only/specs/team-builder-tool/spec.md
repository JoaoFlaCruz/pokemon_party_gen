## REMOVED Requirements

### Requirement: Team builder tool schema
**Reason**: Automatic six-Pokemon team construction is generative AI behavior and must not be exposed as a dedicated MCP tool.
**Migration**: Remove `build_pokemon_team` from MCP registration, listing, dispatch, package exports, and server instructions. Agents should assemble teams themselves using validated data from lower-level tools.

### Requirement: MCP response format
**Reason**: The `build_pokemon_team` MCP tool is being inactivated, so it no longer has a public tool-call response contract.
**Migration**: Calls to `build_pokemon_team` should receive the existing unknown-tool error path. No replacement team-builder MCP response format is introduced.

## MODIFIED Requirements

### Requirement: English team-building documentation
The system SHALL document agentic team-building flow in English while preserving exact tool names, JSON keys, command examples, and behavioral contracts for the remaining tools.

#### Scenario: Documentation is translated
- **WHEN** a maintainer reads the project documentation for architecture, team-building rules, or agentic team flow
- **THEN** the prose is available in English and no longer presents `build_pokemon_team` as an available project tool.

#### Scenario: Technical identifiers are preserved
- **WHEN** documentation references remaining tool names, response fields, role values, commands, file paths, or JSON examples
- **THEN** those identifiers remain exact and are not translated into prose-only equivalents.

#### Scenario: Documentation file names are translated
- **WHEN** Portuguese Markdown documentation files are translated to English
- **THEN** their file names are also renamed to English equivalents and repository references are updated to the new paths.

### Requirement: One-to-five-call agentic flow
The system SHALL document a bounded decision guide for team-building agents using the remaining validation, ranking, moveset, item, and type-relation tools.

#### Scenario: Candidate-first path
- **WHEN** a user asks for a complete team and the AI needs candidate data for open slots
- **THEN** the documentation directs the AI to use `rank_pokemon` with forced Pokemon Champions scope instead of `build_pokemon_team`.

#### Scenario: Deeper validation path
- **WHEN** a user asks for candidate comparison, moveset confidence, type auditing, itemization, or correction of a known weakness
- **THEN** the documentation explains which remaining tools can be used within a bounded validation sequence.

#### Scenario: Avoid unnecessary calls
- **WHEN** a simple request can be satisfied with fewer calls
- **THEN** the documentation directs agents to stop at the lowest call count that satisfies the request and declared validation needs.

### Requirement: Reflection checkpoints
The system SHALL document explicit reflection checkpoints for agentic Pokemon team creation before finalizing a recommendation.

#### Scenario: Initial team reflection
- **WHEN** an agent drafts an initial team from user choices and validated candidate data
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
