## MODIFIED Requirements

### Requirement: Champions-scoped ranking candidates
The system SHALL rank AI-facing Pokemon candidates only within the Pokemon Champions library.

#### Scenario: Ranking without additional filters
- **WHEN** ranking is executed through the MCP `rank_pokemon` tool with no type, ability, or move filters
- **THEN** only Pokemon whose species appears in the Champions Pokédex are scored and returned.

#### Scenario: Ranking with additional filters
- **WHEN** ranking is executed through the MCP `rank_pokemon` tool with type, ability, or move filters
- **THEN** the candidate pool is the intersection of the Champions Pokédex species and the additional filters.

#### Scenario: Ranking output reports scope
- **WHEN** a ranking tool response is returned
- **THEN** the structured output and presentation identify that the candidate pool was scoped to the Pokemon Champions library.

#### Scenario: AI caller cannot disable Champions scope
- **WHEN** an MCP client inspects or calls `rank_pokemon`
- **THEN** the public tool schema does not provide a `champions_only=false` option and the executor uses Champions scope for the ranking request.

