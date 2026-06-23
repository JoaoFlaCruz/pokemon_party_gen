# Research: Desktop Frontend Refactor Without API Integration

## Decision: Build the next phase as frontend-only

**Rationale**: The user requested construction of the two screens without API integration. Keeping this phase frontend-only lets the project validate layout, state transitions, and user workflows before backend contracts are implemented.

**Alternatives considered**:

- Implement HTTP clients immediately: rejected because APIs are not mounted and the user explicitly deferred integration.
- Stub backend endpoints: rejected because it expands the affected layers and creates temporary backend code not needed to validate the screens.

## Decision: Use typed fixture-backed service interfaces

**Rationale**: The UI still needs realistic data shapes for Pokemon summaries, details, moves, natures, items, and saved teams. Service interfaces allow the renderer to call `listPokemon`, `getPokemonDetails`, `saveTeam`, and `listTeams` now, while the implementation behind those calls remains local fixtures. Future API integration can replace the service implementation without changing page components.

**Alternatives considered**:

- Put fixtures directly in components: rejected because it couples UI rendering to data source details.
- Keep global mutable JavaScript state as-is: rejected because it blocks predictable tests and makes migration to API-backed data harder.

## Decision: Represent the app as two primary views

**Rationale**: The requested scope maps cleanly to two screens: Team Assembly and Saved Teams. Navigation between these views is enough to validate save simulation and pagination without introducing routing complexity beyond the desktop app's needs.

**Alternatives considered**:

- Preserve a single-screen app with conditional panels: rejected because the spec explicitly calls out a separate display screen for saved teams.
- Build additional settings or generator screens: rejected as out of scope for this phase.

## Decision: Keep source code TypeScript-only for application logic

**Rationale**: The original request requires rebuilding `desktop_app` using only TypeScript files. This plan permits required toolchain/static files, but all application behavior should live in `.ts` or `.tsx` files under `desktop_app/src/`.

**Alternatives considered**:

- Incrementally convert only `renderer.js`: rejected because it leaves the Electron main process and app boundaries in the old structure.
- Keep JavaScript and add JSDoc types: rejected because it does not satisfy the TypeScript-only requirement.

## Decision: Defer architecture document updates until implementation changes commands/source layout

**Rationale**: This planning step defines the intended layout. During implementation, actual dependency choices, run commands, and test commands must be reflected in `docs/architecture.md` once they are real.

**Alternatives considered**:

- Update architecture docs during planning: rejected because final run/test commands and renderer stack may still be chosen in implementation tasks.

## Decision: Use demo fixtures as UI development data only

**Rationale**: The constitution forbids invented Pokemon facts when real Pokemon data is needed. This phase does not validate Pokemon correctness; it validates UI behavior. Fixtures must be small, deterministic, clearly labeled as demo data, and replaceable by API-backed services.

**Alternatives considered**:

- Query live PokeAPI from the renderer: rejected because this would bypass the intended BFF boundary and violate the no-API-integration scope.
- Generate broad Pokemon catalogs manually: rejected because that risks untraceable or fabricated data.
