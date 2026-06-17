# Data Model: Desktop Frontend Refactor

This model describes frontend state and fixture-backed service data for the two-screen implementation. It does not define database tables or backend persistence.

## Entity: AppView

Fields:

- `currentView`: `"team-builder"` or `"saved-teams"`
- `activeTeamId`: current editable team identifier
- `activeSlotPosition`: integer from 1 to 6

Validation:

- `activeSlotPosition` must always reference an existing slot in the active team.
- Navigation to `saved-teams` must not discard unsaved in-memory edits unless the user explicitly resets them.

## Entity: TeamDraft

Fields:

- `id`: local draft identifier
- `name`: display name
- `slots`: six `TeamSlot` entries ordered by `position`
- `updatedAt`: local timestamp string for UI display or ordering

Relationships:

- Owns exactly six `TeamSlot` records.
- Can be saved into `SavedTeam` by the fixture-backed team service.

Validation:

- Name is required for save simulation.
- Slot positions must be unique integers from 1 to 6.
- Empty slots are allowed.

## Entity: TeamSlot

Fields:

- `position`: integer from 1 to 6
- `pokemonId`: selected Pokemon ID or null
- `level`: integer from 1 to 100
- `gender`: `"male"`, `"female"`, or `"unknown"`
- `natureId`: selected nature ID or null
- `itemId`: selected item ID or null
- `ivPoints`: `IVPointAllocation`
- `moveIds`: ordered list of up to four move IDs

Relationships:

- References `PokemonSummary` and `PokemonDetails` by `pokemonId`.
- References selected `Nature`, `Item`, and `Move` fixture records.

Validation:

- `moveIds` length must be 0 to 4.
- `moveIds` must not contain duplicates.
- Pokemon-specific choices must be cleared or disabled when `pokemonId` is null.

## Entity: PokemonSummary

Fields:

- `id`: numeric Pokemon identifier
- `name`: display/search name
- `pokedexNumber`: integer
- `types`: one or two type IDs
- `spriteUrl`: image reference

Validation:

- Results are sorted by `pokedexNumber` ascending.
- Search filters match against name, Pokedex number, first type, and second type.

## Entity: PokemonDetails

Fields:

- `id`: numeric Pokemon identifier
- `name`: display name
- `pokedexNumber`: integer
- `types`: one or two type IDs
- `baseStats`: `BaseStats`
- `totalStats`: number derived from base stats
- `abilities`: list of ability names
- `moveIds`: list of move IDs available to this Pokemon
- `imageUrl`: artwork reference
- `spriteUrl`: sprite reference
- `description`: display text

Validation:

- `totalStats` equals the sum of base stat values in fixture data.
- One-type Pokemon must remain valid.

## Entity: BaseStats

Fields:

- `hp`
- `attack`
- `defense`
- `specialAttack`
- `specialDefense`
- `speed`

Validation:

- Values must be non-negative integers.

## Entity: IVPointAllocation

Fields:

- `hp`
- `attack`
- `defense`
- `specialAttack`
- `specialDefense`
- `speed`

Validation:

- Values must be non-negative integers.
- Each stat value must be an integer from 0 to 31.
- Total allocation across all six stats must be from 0 to 186.

## Entity: Move

Fields:

- `id`: move identifier
- `name`: display name
- `type`: type ID
- `power`: number or null
- `pp`: number or null
- `description`: display text
- `damageClass`: `"physical"`, `"special"`, or `"status"`

Validation:

- Move selectors show only moves listed for the selected Pokemon.
- Already selected moves are excluded from the remaining move selector options.

## Entity: Nature

Fields:

- `id`: nature identifier
- `name`: display name
- `bonusStat`: stat key or null
- `onusStat`: stat key or null
- `description`: display text

Validation:

- Neutral natures may use null `bonusStat` and `onusStat`.

## Entity: Item

Fields:

- `id`: item identifier
- `name`: display name
- `description`: display text
- `imageUrl`: image reference or null

Validation:

- Missing fixture image URLs must render a clear placeholder state.

## Entity: SavedTeam

Fields:

- `id`: saved team identifier
- `name`: display name
- `slots`: six saved `TeamSlot` snapshots
- `savedAt`: timestamp string
- `contractVersion`: frontend service contract version used when saved

Relationships:

- Created from `TeamDraft` by the fixture-backed save flow.
- Listed by the Saved Teams screen.

Validation:

- Saved-team pagination displays three teams per page.
- Saved teams preserve user selections even if fixture enrichment is incomplete.
- Version mismatches between saved-team data and current frontend service contracts produce diagnostics.

## State Transitions

- `empty slot -> selected slot`: user selects a party slot.
- `selected slot -> configured slot`: user assigns Pokemon, nature, item, stats, or moves.
- `team draft -> saved team`: user activates save and validation passes.
- `team-builder view -> saved-teams view`: user opens saved teams.
- `saved-teams view -> team-builder view`: user returns to editing.
