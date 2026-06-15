## Purpose

Provide a visual desktop interface for Pokemon team generation, selection, trio visualization, moveset suggestions, and team analysis.

## Requirements

### Requirement: Interactive Pokemon selection (Desktop)
The Electron desktop app SHALL allow the user to search, filter, and select between zero and six Pokemon to seed their team.

#### Scenario: Select Pokemon from search
- **WHEN** the user types "Charizard" in the Pokemon search input
- **THEN** the app displays Charizard in the autocomplete list and allows selecting it.

#### Scenario: Lock user-selected Pokemon
- **WHEN** the user selects a Pokemon for the team
- **THEN** that Pokemon is displayed in the selected list with a visual lock icon and a "locked" state.

### Requirement: Visual team generation (Desktop)
The Electron desktop app SHALL request team-building logic from the backend API and render a six-member team.

#### Scenario: Minimal team build action
- **WHEN** the user clicks the "Generate Team" button with less than six Pokemon selected
- **THEN** the app requests the team build from the backend API and populates the remaining slots with AI-selected candidates.

### Requirement: Trio layout presentation (Desktop)
The Electron desktop app SHALL visually display the team organized into a primary trio and a complementary trio in a responsive desktop layout.

#### Scenario: Visual separation of trios
- **WHEN** the generated team is displayed
- **THEN** the screen displays two distinct columns labeled "Primary Trio" and "Complementary Trio".

#### Scenario: Ace Pokemon highlight
- **WHEN** a trio has an identified ace Pokemon
- **THEN** the ace Pokemon is rendered with a prominent badge, card style, or crown icon.

### Requirement: Move ranking and suggestions (Desktop)
The Electron desktop app SHALL display suggested movesets and rankings for each member of the team.

#### Scenario: View moveset details
- **WHEN** the user clicks on a Pokemon card in the team view
- **THEN** the app displays a detailed modal or expandable panel showing the list of ranked movesets, power, accuracy, and type for that Pokemon.

### Requirement: Team analysis dashboard (Desktop)
The Electron desktop app SHALL display team-level statistics and type coverage analysis.

#### Scenario: Type relation matrix
- **WHEN** a team is built
- **THEN** the app dashboard renders a type relation grid/matrix showing the cumulative weaknesses and resistances of the team.
