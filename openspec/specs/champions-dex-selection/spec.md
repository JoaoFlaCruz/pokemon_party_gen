## Purpose

Define how tools discover and enforce Pokemon Champions library membership for candidate selection.
## Requirements
### Requirement: Champions dex membership discovery
The system SHALL discover Pokemon Champions library membership from a PokeAPI-compatible Pokédex resource instead of a hard-coded Pokemon list.

#### Scenario: Discover Champions by identifier
- **WHEN** the system needs the Pokemon Champions library membership
- **THEN** it requests the `pokedex/champions/` resource and reads allowed species from `pokemon_entries[].pokemon_species.name`.

#### Scenario: Discover Champions by numeric fallback
- **WHEN** the configured PokeAPI-compatible source does not resolve the `champions` Pokédex identifier but resolves Pokédex id `36`
- **THEN** the system uses `pokedex/36/` as the fallback Champions membership source.

#### Scenario: Champions membership data unavailable
- **WHEN** neither Champions Pokédex resource can be read from the configured data source
- **THEN** the system reports the data failure instead of inventing allowed Pokemon.

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

### Requirement: Champions membership validation metadata
The system SHALL expose Champions membership status for validated Pokemon when that status affects candidate or team selection.

#### Scenario: Pokemon is inside Champions library
- **WHEN** a validated Pokemon's species is present in the Champions Pokédex
- **THEN** the Pokemon summary can identify it as included in the Champions library.

#### Scenario: Pokemon is outside Champions library
- **WHEN** a validated Pokemon's species is not present in the Champions Pokédex
- **THEN** the Pokemon summary can identify it as outside the Champions library without changing its verified stats or identity.

