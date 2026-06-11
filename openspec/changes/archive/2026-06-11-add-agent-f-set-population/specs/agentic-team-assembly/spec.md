## ADDED Requirements

### Requirement: Active agentic team workflow
The system SHALL document Pokemon team assembly as an agentic workflow that uses lower-level data tools and does not use the inactive `build_pokemon_team` MCP tool.

#### Scenario: Team builder tool remains inactive
- **WHEN** the workflow documentation or skill instructions describe six-Pokemon team creation
- **THEN** they do not instruct agents to call `build_pokemon_team` and instead describe team assembly as an AI workflow using available lower-level tools.

#### Scenario: Lower-level data tools remain available
- **WHEN** agents need Pokemon candidates, moves, type relations, or item data
- **THEN** the workflow directs them to use the existing lower-level tools through the documented agent responsibilities.

### Requirement: Agent F set population
The system SHALL define Agent F as the Set Populator responsible for detailed per-Pokemon set data after team composition and roles are stable.

#### Scenario: Agent F runs after validation
- **WHEN** Agents B, C, D, and E produce a stable six-Pokemon draft with roles and trio strategies
- **THEN** Agent F populates each Pokemon's moves, EVs, nature, item, and usage suggestion according to the role and strategy.

#### Scenario: Agent F reruns after refinement
- **WHEN** a later refinement changes a Pokemon, role, trio strategy, or important team gap
- **THEN** Agent F revisits affected Pokemon and updates their detailed set data before final response.

#### Scenario: Agent F requests missing data
- **WHEN** Agent F needs move, item, Pokemon, or type data that has not been validated
- **THEN** the workflow routes the data need through Agent A or records the unresolved detail in `pending`.

### Requirement: Detailed member output
The system SHALL require every final team member to include detailed strategy-aligned fields when enough validated data and confidence are available.

#### Scenario: Human-readable member fields
- **WHEN** the system presents a final team in human-readable text
- **THEN** each Pokemon includes `Nome`, `role`, `Motivo`, `Golpes`, `EVs`, `Natureza`, `Item`, and `Sugestao`.

#### Scenario: Four moves with reasons
- **WHEN** Agent F recommends moves for a Pokemon
- **THEN** it provides exactly four moves and a reason for each move.

#### Scenario: EV spread with point values
- **WHEN** Agent F recommends EVs for a Pokemon
- **THEN** it provides named stat allocations with point values that support the Pokemon's role and strategy.

#### Scenario: Pending unsupported set data
- **WHEN** Agent F cannot validate or confidently justify a move, EV spread, nature, or item
- **THEN** it does not invent that detail and records the uncertainty in `pending`.

### Requirement: Create single team skill alignment
The system SHALL update `.codex/skills/create-single-team/SKILL.md` so Codex follows the active six-agent workflow and final detailed output contract.

#### Scenario: Skill uses Agent F
- **WHEN** Codex uses the `create-single-team` skill to generate one or more single-battle teams
- **THEN** the skill instructions include Agent F after team validation and before final response.

#### Scenario: Skill final response includes detailed sets
- **WHEN** the `create-single-team` skill defines its response format
- **THEN** each Pokemon slot includes the detailed fields populated by Agent F.
