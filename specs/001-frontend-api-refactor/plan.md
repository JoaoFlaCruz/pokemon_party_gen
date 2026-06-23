# Implementation Plan: Desktop Frontend Refactor Without API Integration

**Branch**: `[001-frontend-api-refactor]` | **Date**: 2026-06-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-frontend-api-refactor/spec.md`

**Planning Focus**: Develop the frontend refactor for the two desktop screens first: team assembly and saved-team display. Backend/API integration is explicitly deferred; this phase uses typed local fixtures and frontend service contracts that can later be backed by HTTP APIs.

## Summary

Refactor `desktop_app` from loose Electron JavaScript files into a TypeScript-only application source layout that presents two usable desktop screens: a team assembly screen and a saved-team display screen. The implementation will preserve the existing Pokemon team-building workflow while introducing typed state, reusable UI components, deterministic fixture data, and frontend service interfaces that match the future API planning document. No Python BFF, persistence API, PokeAPI HTTP calls, or MCP tool changes are implemented in this phase.

## Technical Context

**Language/Version**: TypeScript application source for Electron desktop; existing runtime is Electron `^42.4.0` from `desktop_app/package.json`.

**Primary Dependencies**: Electron; TypeScript; React/TSX for the renderer; Vite for renderer build/dev bundling; Vitest and Testing Library for frontend tests; local fixture-data service. No BFF/API dependency for this phase.

**Storage**: In-memory frontend state with optional local fixture seed data only. No database, file persistence, or FastAPI storage integration in this phase.

**Testing**: Type checks; frontend unit tests for state reducers/services; component/workflow tests for the two screens; fixture contract tests; lightweight timing assertions for fixture interactions where practical; Electron smoke test. Existing Python unit tests are not expected to exercise this frontend-only change.

**Target Platform**: Desktop Electron app under `desktop_app/`.

**Project Type**: Desktop frontend refactor with future Python BFF/API contracts documented but not integrated.

**Affected Layers**: Electron UI and documentation/spec artifacts. Python BFF/API, application use cases, infrastructure/PokeAPI adapters, and MCP tools are out of scope for this implementation phase.

**Public Contracts**: Frontend UI contracts and TypeScript service interfaces for fixture-backed data. HTTP contracts remain documented in `docs/project/frontend-api-contracts.md` for future backend work but are not consumed at runtime in this phase.

**Data Sources**: Typed local fixture data derived from a small, clearly labeled sample set for UI development. Fixture Pokemon facts must include a source note pointing to a PokeAPI-compatible source snapshot or existing project fixture when factual values are displayed; fixture facts must not be expanded with invented competitive claims.

**Performance Goals**: Team assembly interactions update within 100 ms for fixture data; screen navigation completes within 300 ms; fixture search/filtering handles at least 50 Pokemon summaries without visible delay.

**Constraints**: Application source introduced by this refactor must be TypeScript or TSX; no live API calls; no backend changes; no fabricated claim that demo fixture data is complete Pokemon source data; IV point controls must enforce 0-31 per stat and 186 total points; two screens must be usable without running a local API.

**Scale/Scope**: Two desktop screens, one shared application state model, local service interfaces for Pokemon catalog, nature catalog, item catalog, moves, compatibility metadata, team save simulation, and saved-team listing.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Layered Architecture**: PASS. Only the Electron UI layer is implemented. Future API boundaries are represented as frontend service interfaces and docs; the UI will not call PokeAPI directly.
- **Contract-First Boundaries**: PASS. UI workflow contracts and service interfaces are planned in `contracts/`; future HTTP contracts already exist in `docs/project/frontend-api-contracts.md`.
- **TDD Plan**: PASS. First tests should cover screen navigation, slot selection, filters, move uniqueness, stat validation, save simulation, and pagination using fixtures.
- **Documentation Plan**: PASS. Spec Kit artifacts, quickstart, contracts, and `docs/project/frontend-api-contracts.md` cover this phase. `docs/architecture.md` should be updated during implementation if the desktop source structure or run/test commands change.
- **Data Fidelity**: PASS WITH CONSTRAINT. Runtime uses demo fixtures because live API integration is deferred. Fixtures must be explicitly labeled, small, deterministic, source-noted for factual Pokemon values, and not presented as complete source truth.
- **Manual Checks**: PASS. Manual Electron validation is required; local PokeAPI validation is not part of this phase.

## Project Structure

### Documentation (this feature)

```text
specs/001-frontend-api-refactor/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── frontend-services.md
│   ├── ui-workflows.md
│   └── fixture-data.md
└── tasks.md
```

### Source Code (repository root)

```text
desktop_app/
├── package.json
├── package-lock.json
├── tsconfig.json
├── index.html
├── src/
│   ├── main/
│   │   ├── main.ts
│   │   └── preload.ts
│   └── renderer/
│       ├── app.tsx
│       ├── components/
│       ├── data/
│       ├── pages/
│       ├── services/
│       ├── state/
│       ├── styles/
│       └── types/
└── tests/
    ├── renderer/
    └── smoke/

docs/project/
├── descritivo.md
└── frontend-api-contracts.md
```

**Structure Decision**: Use a single Electron app under `desktop_app/` with TypeScript main/preload/renderer source and a React/TSX renderer built through Vite. All app source must stay under `desktop_app/src/` and keep service interfaces separate from UI components so future API integration replaces fixtures without rewriting screens.

## Phase 0: Research

Research output: [research.md](./research.md)

Key resolved decisions:

- Use local typed fixtures for this frontend phase.
- Implement two explicit renderer views: Team Assembly and Saved Teams.
- Use service interfaces that mirror future API operations but return fixture-backed promises and compatibility metadata.
- Defer Python BFF/API work, persistence, and PokeAPI integration to later specs/tasks.

## Phase 1: Design & Contracts

Design outputs:

- [data-model.md](./data-model.md)
- [contracts/frontend-services.md](./contracts/frontend-services.md)
- [contracts/ui-workflows.md](./contracts/ui-workflows.md)
- [contracts/fixture-data.md](./contracts/fixture-data.md)
- [quickstart.md](./quickstart.md)

## Post-Design Constitution Check

- **Layered Architecture**: PASS. The design keeps frontend service interfaces inside `desktop_app` and avoids backend or PokeAPI direct calls.
- **Contract-First Boundaries**: PASS. Frontend service, UI workflow, and fixture contracts are defined before implementation.
- **TDD Plan**: PASS. Quickstart and contracts define tests and manual checks to write before implementation work.
- **Documentation Plan**: PASS. Design artifacts exist; implementation must update architecture docs if source layout and commands change.
- **Data Fidelity**: PASS WITH DOCUMENTED LIMITATION. Fixtures are demo-only, must include source notes for factual Pokemon values, and must be named as such in code/UI test context.
- **Manual Checks**: PASS. Electron manual validation is documented separately from automated validation.

## Complexity Tracking

No constitution violations require justification for this phase.
