# Feature Specification: Desktop Team Builder Frontend Refactor

**Feature Branch**: `[001-frontend-api-refactor]`

**Created**: 2026-06-17

**Status**: Draft

**Input**: User description: "Leia o arquivo de documentação docs/project/descritivo.md e planeje uma refatoração do frontend em desktop_app de modo a reconstituir o projeto em arquitetura moderna usando apenas arquivos em Typescript. As APIs não estão montadas, dessa forma você deve montar um documento em docs/project para explicar cada API a ser construída e montada. Desenvolva a refatoração do frontend com foco na construção das duas telas, sem integração com API ainda. Aplique correções ao planejamento de modo a obter mais coerência no plano de execução."

## Scope Clarification

This feature delivers the frontend-only phase for the desktop team builder. The two screens must work without a running backend by using clearly labeled demo fixture data and local save simulation. Backend APIs, real persistence, live PokeAPI access, and API version negotiation remain documented future work and must not be implemented in this phase.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assemble a Pokemon team (Priority: P1)

A player builds a six-Pokemon team from the desktop screen, selects a team slot, searches Pokemon by name, Pokedex number, and type filters, and sees the selected Pokemon's details immediately after selection.

**Why this priority**: This is the primary workflow described for the product and must work before team persistence or browsing saved teams has value.

**Independent Test**: Can be tested by opening the desktop screen, filtering the Pokemon list, selecting one Pokemon into an empty slot, and verifying that the party slot, sprite, details panel, stats, moves, abilities, and Pokedex text are populated from traceable Pokemon data.

**Acceptance Scenarios**:

1. **Given** an empty team slot and available Pokemon data, **When** the player filters by Pokemon name and selects a result, **Then** the slot displays that Pokemon's sprite and the details panel displays name, types, base stats, total stats, available moves, abilities, image, and description.
2. **Given** a Pokemon list with type and Pokedex filters, **When** the player changes any filter value, **Then** the displayed list refreshes in ascending Pokedex order and only includes matching Pokemon.
3. **Given** demo fixture details are unavailable for a listed Pokemon, **When** the player attempts to select that Pokemon, **Then** the screen shows an explicit unavailable-data diagnostic and does not invent Pokemon details.

---

### User Story 2 - Configure Pokemon choices (Priority: P2)

A player configures each selected Pokemon by choosing a nature, held item, distributed IV points, and up to four unique moves, while keeping those choices attached to the correct team slot.

**Why this priority**: Custom choices define the user's actual team and must be captured before a team can be saved or reviewed meaningfully.

**Independent Test**: Can be tested by selecting a Pokemon, assigning a nature, item, IV points, and four moves, then switching slots and returning to confirm the selected values remain associated with that Pokemon.

**Acceptance Scenarios**:

1. **Given** a selected Pokemon with available move data, **When** the player selects a move for one of four move fields, **Then** the move appears in that field, its description is available on hover or focus, and it is excluded from the remaining selectable moves for that Pokemon.
2. **Given** available nature data, **When** the player opens the nature selector, **Then** each option displays name, increased stat, decreased stat, and description.
3. **Given** available item data, **When** the player opens the item selector, **Then** each option displays name, description, and image reference, and the selected item appears in the Pokemon details panel.
4. **Given** IV point limits are reached or invalid values are entered, **When** the player changes distributed points, **Then** invalid values are rejected with a clear message and previously valid values remain intact.

---

### User Story 3 - Save and browse teams (Priority: P3)

A player saves a completed or partially completed team in the frontend session and later browses saved teams in pages of three teams, with each team showing its six Pokemon and user-selected customizations.

**Why this priority**: Persistence turns the builder from a temporary screen into a usable team management tool, but it depends on the assembly and configuration flows.

**Independent Test**: Can be tested by saving at least four teams, opening the team display screen, confirming three teams appear on the first page, and navigating to the next page to see the remaining team.

**Acceptance Scenarios**:

1. **Given** a team with at least one configured Pokemon, **When** the player saves the team, **Then** the team is stored for the current frontend session with name, six ordered slots, Pokemon identities, IV points, moves, items, and nature selections.
2. **Given** more than three saved teams exist, **When** the player opens the team display screen, **Then** teams are paginated three per page and navigation preserves the saved ordering.
3. **Given** a saved team references Pokemon data that is temporarily unavailable, **When** the player views that team, **Then** saved user choices remain visible and unavailable external details are marked as pending or unavailable.

---

### Edge Cases

- The Pokemon list returns no matches for the active filters.
- A selected Pokemon has fewer than four available moves in the configured source data.
- The same move is selected twice for the same Pokemon.
- A Pokemon has one type instead of two.
- Nature, item, move, or Pokemon detail data is incomplete or unavailable from the demo fixture source.
- The user attempts to save a team with empty slots.
- A saved team references a Pokemon, move, item, or nature that no longer appears in the current source data.
- Future API compatibility metadata is unavailable or mismatched in the frontend service contract; the user must see an actionable diagnostic rather than a broken screen.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a desktop team assembly screen with one active Pokemon details panel and six ordered party slots.
- **FR-002**: Users MUST be able to select any party slot and make that slot the target for Pokemon, move, item, nature, and IV point changes.
- **FR-003**: System MUST list Pokemon with filters for first type, second type, name, and Pokedex number.
- **FR-004**: System MUST refresh Pokemon search results whenever filter input changes and display results in ascending Pokedex order.
- **FR-005**: System MUST fetch and display selected Pokemon details including name, types, base stats, computed total stats, available moves, abilities, image reference, and Pokedex description.
- **FR-006**: System MUST list available natures with name, increased stat, decreased stat, and description.
- **FR-007**: System MUST list selectable held items with name, description, and image reference.
- **FR-008**: Users MUST be able to assign up to four unique moves to a selected Pokemon from that Pokemon's available move list.
- **FR-009**: System MUST display move details including name, type, power, PP, description, and attack category.
- **FR-010**: System MUST prevent duplicate moves within the same Pokemon and keep already selected moves out of the remaining move choices.
- **FR-011**: Users MUST be able to assign and edit IV points for each Pokemon, with each stat limited to 0-31 points and total IV allocation limited to 186 points.
- **FR-012**: Users MUST be able to save teams for the current frontend session with name, ordered slots, Pokemon identity, IV points, selected moves, selected item, selected nature, and source-data references required for later display.
- **FR-013**: System MUST provide a saved-team display screen that lists saved teams with pagination of three teams per page.
- **FR-014**: System MUST preserve user-selected values separately from external Pokemon facts so saved teams remain understandable when external data is pending.
- **FR-015**: System MUST return explicit diagnostics for missing, incomplete, unavailable, or incompatible data rather than fabricating Pokemon facts.
- **FR-016**: System MUST define stable frontend service contracts for Pokemon listing, Pokemon details, natures, items, move details, team save simulation, and saved-team listing before implementation; HTTP API contracts remain future work.
- **FR-017**: System MUST keep the existing desktop workflows recognizable while allowing the internal desktop source organization to be rebuilt.

### Key Entities *(include if feature involves data)*

- **Team**: A named collection of up to six ordered Pokemon slots, plus saved metadata needed to display and paginate teams.
- **Team Slot**: One position in a team containing optional Pokemon identity, user-selected customizations, and display state.
- **Pokemon Summary**: Search-list representation containing Pokedex number, name, types, and sprite reference.
- **Pokemon Details**: Full representation used in the details panel, including types, stats, total stats, abilities, moves, images, and description.
- **Move**: Selectable Pokemon attack containing name, type, power, PP, description, and physical or special category.
- **Nature**: Selectable Pokemon modifier containing name, bonus stat, penalty stat, and description.
- **Item**: Selectable held item containing name, description, and image reference.
- **IV Point Allocation**: User-entered points distributed across Pokemon stats and validated against 0-31 per stat and 186 total points.

### Public Contracts *(mandatory if any boundary changes)*

- **Pokemon Search Contract**: Frontend service accepts optional type, name, and Pokedex number filters; returns ordered Pokemon summaries, paging metadata if needed, and diagnostics for unavailable fixture data.
- **Pokemon Details Contract**: Frontend service accepts a Pokemon identifier; returns details required by the active Pokemon panel and diagnostics when fixture facts are missing.
- **Nature Catalog Contract**: Frontend service returns all selectable natures with display fields and diagnostics.
- **Item Catalog Contract**: Frontend service returns all selectable held items with display fields and diagnostics.
- **Move Catalog Contract**: Frontend service accepts a Pokemon identifier; returns selectable moves for that Pokemon with display fields and diagnostics.
- **Team Save Simulation Contract**: Frontend service accepts a team payload with ordered slots and user choices; returns saved team identity, validation results, and diagnostics for the current session.
- **Saved Team Listing Contract**: Frontend service accepts pagination inputs; returns three saved teams per page by default with paging metadata and diagnostics.
- **Input Validation**: Invalid identifiers, unsupported filters, duplicate moves, out-of-range IV points, malformed team slots, and incompatible contract versions must return structured validation errors.
- **Response Shape**: All successful and failed responses must be JSON-serializable and include enough diagnostics for the desktop client to show user-facing pending or error states.
- **Compatibility**: Frontend service contract metadata must include a version marker so the desktop client can display diagnostics for future API mismatches without blocking the fixture-only phase.

### Data Sources & Fidelity *(mandatory if Pokemon data is involved)*

- **Source**: In this frontend-only phase, Pokemon facts shown by fixtures must be traceable demo/test data copied from a named PokeAPI-compatible source snapshot or existing project fixture. Future production behavior must come from configured PokeAPI-compatible data through the Python BFF/API layer; future saved user choices must come from the application persistence layer.
- **Facts Required**: Pokemon identity, Pokedex number, types, stats, computed total stats, moves, abilities, natures, held items, descriptions, and image references.
- **Missing Data Behavior**: Missing or unavailable fixture or future source data must be shown as diagnostics or pending states; fabricated Pokemon facts are forbidden.

### Documentation Requirements *(mandatory)*

- **Docs to Update**: Keep the project API planning document under `docs/project`; update `docs/architecture.md` during implementation when desktop source structure, run commands, test commands, or frontend service contracts change.
- **Run/Test Notes**: Planning must document desktop run commands, frontend fixture validation, future backend API run commands, contract validation expectations, and automated tests for desktop workflows.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can search for a Pokemon, assign it to a team slot, and see its details in under 10 seconds during normal local development conditions.
- **SC-002**: A user can configure one Pokemon with nature, item, IV points, and four unique moves without losing changes when switching between team slots.
- **SC-003**: A user can save a team and find it again in the saved-team display screen in under 30 seconds.
- **SC-004**: Saved-team browsing consistently shows no more than three teams per page and exposes navigation whenever more pages are available.
- **SC-005**: 100% of unavailable Pokemon, move, item, nature, or saved-team data cases produce explicit diagnostics rather than fabricated data.
- **SC-006**: At least 90% of primary workflow acceptance scenarios pass in automated or repeatable manual validation before implementation is considered complete.
- **SC-007**: Fixture-backed search, slot selection, screen navigation, and saved-team pagination complete without visible delay during manual desktop validation.

## Assumptions

- The first planned release targets desktop usage only; mobile and web deployment are out of scope.
- The current visual concept and core workflows of the existing desktop app should be preserved unless a later design decision changes them.
- Demo fixtures are used only for this frontend phase; the Python BFF/API layer will mediate future access to PokeAPI-compatible data, and a persistence API will store user-created team data in a later phase.
- User authentication and multi-user permissions are out of scope unless introduced by a later requirement.
- Empty team slots may be saved, but validation must clearly distinguish empty slots from invalid Pokemon selections.
- API contracts may be implemented incrementally in a later phase, but the desktop app must use documented frontend service contracts rather than direct external Pokemon calls.
