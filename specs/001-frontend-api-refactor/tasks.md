# Tasks: Desktop Team Builder Frontend Refactor

**Input**: Design documents from `specs/001-frontend-api-refactor/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/)

**Tests**: Mandatory for this feature because the project constitution requires TDD for behavior changes. Write tests first, confirm they fail, then implement.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish TypeScript Electron app structure, build tooling, and test tooling.

- [X] T001 Update desktop dependencies and scripts for Electron, TypeScript, React, Vite, Vitest, and Testing Library in `desktop_app/package.json`
- [X] T002 Install dependencies and refresh lockfile in `desktop_app/package-lock.json`
- [X] T003 Create TypeScript compiler configuration for Electron and renderer source in `desktop_app/tsconfig.json`
- [X] T004 Create Vite renderer configuration in `desktop_app/vite.config.ts`
- [X] T005 Create Vitest setup configuration in `desktop_app/vitest.config.ts`
- [X] T006 [P] Create test DOM setup file in `desktop_app/tests/setup.ts`
- [X] T007 [P] Replace legacy HTML script entry with Vite renderer mount point in `desktop_app/index.html`
- [X] T008 [P] Create Electron TypeScript main process entry in `desktop_app/src/main/main.ts`
- [X] T009 [P] Create Electron preload boundary in `desktop_app/src/main/preload.ts`
- [X] T010 Create renderer bootstrap entry in `desktop_app/src/renderer/main.tsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared types, fixtures, services, state, and layout primitives required by every user story.

**Critical**: No user story work should begin until this phase is complete.

- [X] T011 [P] Define shared domain, diagnostic, and `contractVersion` service result types in `desktop_app/src/renderer/types/domain.ts`
- [X] T012 [P] Define app view, team draft, saved team, and action types in `desktop_app/src/renderer/types/app-state.ts`
- [X] T013 [P] Add source-noted demo Pokemon, move, nature, item, and saved-team fixtures in `desktop_app/src/renderer/data/demo-fixtures.ts`
- [X] T014 [P] Add fixture contract tests for required fixture counts, source notes, and demo-data constraints in `desktop_app/tests/renderer/demo-fixtures.test.ts`
- [X] T015 [P] Implement Pokemon catalog fixture service in `desktop_app/src/renderer/services/pokemonCatalogService.ts`
- [X] T016 [P] Implement nature and item catalog fixture service in `desktop_app/src/renderer/services/catalogService.ts`
- [X] T017 [P] Implement team repository fixture service with in-memory saved teams in `desktop_app/src/renderer/services/teamRepository.ts`
- [X] T018 Add service contract tests for filtering, diagnostics, compatibility metadata, save validation, and pagination in `desktop_app/tests/renderer/services.test.ts`
- [X] T019 Implement app state reducer and action creators in `desktop_app/src/renderer/state/appState.ts`
- [X] T020 Add reducer tests for view navigation, active slot selection, slot updates, save results, and diagnostics in `desktop_app/tests/renderer/appState.test.ts`
- [X] T021 [P] Create shared shell, navigation, diagnostic banner, and empty-state components in `desktop_app/src/renderer/components/AppShell.tsx`
- [X] T022 [P] Create global desktop styling foundation in `desktop_app/src/renderer/styles/app.css`
- [X] T023 Wire application root with fixture services, reducer state, and view switching in `desktop_app/src/renderer/app.tsx`

**Checkpoint**: The desktop app can render a shell with fixture-backed services and tests can run without a backend.

---

## Phase 3: User Story 1 - Assemble a Pokemon Team (Priority: P1) MVP

**Goal**: Users can open the Team Assembly screen, filter Pokemon, select a party slot, assign a Pokemon, and see details populated from fixture services.

**Independent Test**: Open the desktop screen, filter Pokemon by name/type/Pokedex number, select a result into an empty slot, and verify the slot, sprite, details panel, stats, abilities, moves, image, and description update without any API running.

### Tests for User Story 1

- [X] T024 [P] [US1] Add Pokemon filter and Pokedex ordering tests in `desktop_app/tests/renderer/teamBuilderFilters.test.tsx`
- [X] T025 [P] [US1] Add slot selection and Pokemon assignment workflow tests in `desktop_app/tests/renderer/teamBuilderAssignment.test.tsx`
- [X] T026 [P] [US1] Add missing Pokemon details diagnostic UI test in `desktop_app/tests/renderer/teamBuilderDiagnostics.test.tsx`

### Implementation for User Story 1

- [X] T027 [P] [US1] Create party slot grid component in `desktop_app/src/renderer/components/PartySlotGrid.tsx`
- [X] T028 [P] [US1] Create active Pokemon detail panel component in `desktop_app/src/renderer/components/PokemonDetailPanel.tsx`
- [X] T029 [P] [US1] Create Pokemon search and filter component in `desktop_app/src/renderer/components/PokemonSearchPanel.tsx`
- [X] T030 [US1] Implement Team Assembly page composition in `desktop_app/src/renderer/pages/TeamBuilderPage.tsx`
- [X] T031 [US1] Connect Pokemon filtering and active-slot assignment actions in `desktop_app/src/renderer/state/appState.ts`
- [X] T032 [US1] Render fixture diagnostics and empty filter results in `desktop_app/src/renderer/pages/TeamBuilderPage.tsx`
- [X] T033 [US1] Integrate Team Assembly as the default view in `desktop_app/src/renderer/app.tsx`

**Checkpoint**: User Story 1 is independently functional and is the MVP.

---

## Phase 4: User Story 2 - Configure Pokemon Choices (Priority: P2)

**Goal**: Users can configure the selected Pokemon with nature, item, IV points, and up to four unique moves while preserving those choices per slot.

**Independent Test**: Select a Pokemon, assign nature, item, IV points, and four moves, switch to another slot, return to the original slot, and verify all selected values remain attached to that Pokemon.

### Tests for User Story 2

- [X] T034 [P] [US2] Add move uniqueness and move description tests in `desktop_app/tests/renderer/moveSelection.test.tsx`
- [X] T035 [P] [US2] Add nature and item selector workflow tests in `desktop_app/tests/renderer/natureItemSelection.test.tsx`
- [X] T036 [P] [US2] Add IV point validation for 0-31 per stat, 186 total, and slot persistence tests in `desktop_app/tests/renderer/statPointAllocation.test.tsx`

### Implementation for User Story 2

- [X] T037 [P] [US2] Create move selector group with hover/focus description display in `desktop_app/src/renderer/components/MoveSelectorGroup.tsx`
- [X] T038 [P] [US2] Create nature selector component in `desktop_app/src/renderer/components/NatureSelector.tsx`
- [X] T039 [P] [US2] Create item selector component with missing-image placeholder state in `desktop_app/src/renderer/components/ItemSelector.tsx`
- [X] T040 [P] [US2] Create IV point allocation controls in `desktop_app/src/renderer/components/StatPointControls.tsx`
- [X] T041 [US2] Add slot customization validation rules including IV limits in `desktop_app/src/renderer/state/appState.ts`
- [X] T042 [US2] Integrate nature, item, stat, and move controls into `desktop_app/src/renderer/pages/TeamBuilderPage.tsx`
- [X] T043 [US2] Ensure selected Pokemon customizations persist across slot changes in `desktop_app/src/renderer/state/appState.ts`

**Checkpoint**: User Stories 1 and 2 both work independently in the Team Assembly screen.

---

## Phase 5: User Story 3 - Save and Browse Teams (Priority: P3)

**Goal**: Users can save the current team draft, open the Saved Teams screen, and browse saved teams three per page.

**Independent Test**: Save at least four teams, open Saved Teams, confirm three teams appear on page 1, navigate to page 2, and return to Team Assembly without losing the current draft.

### Tests for User Story 3

- [X] T044 [P] [US3] Add save team validation and saved-state tests in `desktop_app/tests/renderer/saveTeam.test.tsx`
- [X] T045 [P] [US3] Add saved-team pagination workflow tests in `desktop_app/tests/renderer/savedTeamsPagination.test.tsx`
- [X] T046 [P] [US3] Add saved-team missing enrichment and compatibility diagnostic tests in `desktop_app/tests/renderer/savedTeamDiagnostics.test.tsx`

### Implementation for User Story 3

- [X] T047 [P] [US3] Create save team button and validation summary component in `desktop_app/src/renderer/components/SaveTeamControls.tsx`
- [X] T048 [P] [US3] Create saved team card component with six-slot summary in `desktop_app/src/renderer/components/SavedTeamCard.tsx`
- [X] T049 [P] [US3] Create pagination controls component in `desktop_app/src/renderer/components/PaginationControls.tsx`
- [X] T050 [US3] Implement Saved Teams page in `desktop_app/src/renderer/pages/SavedTeamsPage.tsx`
- [X] T051 [US3] Connect save and list saved teams actions to fixture team repository in `desktop_app/src/renderer/state/appState.ts`
- [X] T052 [US3] Add navigation between Team Assembly and Saved Teams in `desktop_app/src/renderer/app.tsx`
- [X] T053 [US3] Render saved-team empty state and missing enrichment diagnostics in `desktop_app/src/renderer/pages/SavedTeamsPage.tsx`

**Checkpoint**: All user stories are independently functional with fixture-backed frontend behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, cleanup, and regression checks across all stories.

- [X] T054 [P] Remove or quarantine obsolete legacy renderer code after TypeScript replacement in `desktop_app/renderer.js`
- [X] T055 [P] Remove or quarantine obsolete legacy main process code after TypeScript replacement in `desktop_app/main.js`
- [X] T056 [P] Update desktop run, build, typecheck, and test commands in `docs/architecture.md`
- [X] T057 [P] Update frontend API planning notes to mark this phase as fixture-only in `docs/project/frontend-api-contracts.md`
- [X] T058 Run TypeScript typecheck and fix any issues in `desktop_app/src/`
- [X] T059 Run frontend tests and fix any issues in `desktop_app/tests/renderer/`
- [X] T060 Run Electron manual smoke validation including visible-delay timing checks and record residual risks in `specs/001-frontend-api-refactor/quickstart.md`
- [X] T061 Run existing Python unit tests to confirm frontend work did not affect backend behavior in `mcp_server/tests/`
- [X] T062 [P] Add repeatable fixture interaction timing smoke tests for search, slot selection, navigation, and pagination in `desktop_app/tests/renderer/performanceSmoke.test.tsx`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1; blocks every user story.
- **Phase 3 US1**: Depends on Phase 2 and is the MVP.
- **Phase 4 US2**: Depends on Phase 2; uses Team Assembly components from US1 for final integration.
- **Phase 5 US3**: Depends on Phase 2; save command integrates most naturally after US1 and US2.
- **Phase 6 Polish**: Depends on completed selected user stories.

### User Story Dependencies

- **US1 Assemble a Pokemon team**: Can start after Phase 2; no dependency on US2 or US3.
- **US2 Configure Pokemon choices**: Can start after Phase 2, but final integration into `TeamBuilderPage.tsx` is simpler after US1 page composition exists.
- **US3 Save and browse teams**: Can start after Phase 2, but full validation benefits from US1 and US2 state paths.

### Within Each User Story

- Tests must be written first and fail before implementation.
- Types and fixture services precede components.
- Components precede page composition.
- Page composition precedes app-level routing/navigation.

---

## Parallel Opportunities

- Setup tasks T006-T009 can run in parallel after dependency updates are planned.
- Foundational type, fixture, service, and shared component tasks T011-T017 and T021-T022 can run in parallel.
- US1 tests T024-T026 can run in parallel, then components T027-T029 can run in parallel.
- US2 tests T034-T036 can run in parallel, then components T037-T040 can run in parallel.
- US3 tests T044-T046 can run in parallel, then components T047-T049 can run in parallel.
- Polish documentation tasks T056-T057 can run in parallel with code cleanup tasks T054-T055 and timing test task T062.

## Parallel Example: User Story 1

```text
Task: "T024 [P] [US1] Add Pokemon filter and Pokedex ordering tests in desktop_app/tests/renderer/teamBuilderFilters.test.tsx"
Task: "T025 [P] [US1] Add slot selection and Pokemon assignment workflow tests in desktop_app/tests/renderer/teamBuilderAssignment.test.tsx"
Task: "T026 [P] [US1] Add missing Pokemon details diagnostic UI test in desktop_app/tests/renderer/teamBuilderDiagnostics.test.tsx"
Task: "T027 [P] [US1] Create party slot grid component in desktop_app/src/renderer/components/PartySlotGrid.tsx"
Task: "T028 [P] [US1] Create active Pokemon detail panel component in desktop_app/src/renderer/components/PokemonDetailPanel.tsx"
Task: "T029 [P] [US1] Create Pokemon search and filter component in desktop_app/src/renderer/components/PokemonSearchPanel.tsx"
```

## Parallel Example: User Story 2

```text
Task: "T034 [P] [US2] Add move uniqueness and move description tests in desktop_app/tests/renderer/moveSelection.test.tsx"
Task: "T035 [P] [US2] Add nature and item selector workflow tests in desktop_app/tests/renderer/natureItemSelection.test.tsx"
Task: "T036 [P] [US2] Add IV point validation and slot persistence tests in desktop_app/tests/renderer/statPointAllocation.test.tsx"
Task: "T037 [P] [US2] Create move selector group with hover/focus description display in desktop_app/src/renderer/components/MoveSelectorGroup.tsx"
Task: "T038 [P] [US2] Create nature selector component in desktop_app/src/renderer/components/NatureSelector.tsx"
Task: "T039 [P] [US2] Create item selector component with missing-image placeholder state in desktop_app/src/renderer/components/ItemSelector.tsx"
Task: "T040 [P] [US2] Create IV point allocation controls in desktop_app/src/renderer/components/StatPointControls.tsx"
```

## Parallel Example: User Story 3

```text
Task: "T044 [P] [US3] Add save team validation and saved-state tests in desktop_app/tests/renderer/saveTeam.test.tsx"
Task: "T045 [P] [US3] Add saved-team pagination workflow tests in desktop_app/tests/renderer/savedTeamsPagination.test.tsx"
Task: "T046 [P] [US3] Add saved-team missing enrichment and compatibility diagnostic tests in desktop_app/tests/renderer/savedTeamDiagnostics.test.tsx"
Task: "T047 [P] [US3] Create save team button and validation summary component in desktop_app/src/renderer/components/SaveTeamControls.tsx"
Task: "T048 [P] [US3] Create saved team card component with six-slot summary in desktop_app/src/renderer/components/SavedTeamCard.tsx"
Task: "T049 [P] [US3] Create pagination controls component in desktop_app/src/renderer/components/PaginationControls.tsx"
```

---

## Implementation Strategy

### MVP First: User Story 1

1. Complete Phase 1 setup.
2. Complete Phase 2 foundation.
3. Complete Phase 3 US1 tests and implementation.
4. Validate Team Assembly can filter fixture Pokemon, assign a Pokemon to a slot, and show details without an API.
5. Stop and demo before continuing to US2.

### Incremental Delivery

1. US1 delivers the usable team assembly shell and Pokemon selection.
2. US2 adds user customization for natures, items, IV points, and moves.
3. US3 adds save simulation and Saved Teams pagination.
4. Polish updates docs, removes legacy entry points, and verifies all checks.

### Notes

- Fixture data is demo-only, must include source notes for factual Pokemon values, and must not be described as complete Pokemon source truth.
- Do not add Python BFF, FastAPI, PokeAPI, persistence, or MCP implementation in this task set.
- Update `docs/architecture.md` when implementation changes real desktop commands, dependencies, or source layout.
- Keep new application behavior under `desktop_app/src/` as TypeScript or TSX.
