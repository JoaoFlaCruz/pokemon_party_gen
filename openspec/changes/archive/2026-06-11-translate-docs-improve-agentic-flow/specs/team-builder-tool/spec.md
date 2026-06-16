## ADDED Requirements

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
