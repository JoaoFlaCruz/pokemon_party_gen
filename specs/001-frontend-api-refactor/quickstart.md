# Quickstart: Validate Frontend Refactor

This guide validates the frontend-only implementation of the two desktop screens. It assumes API integration is not present.

## Prerequisites

- Node.js/npm available for `desktop_app`.
- Existing repository dependencies installed or installable through npm.
- No local Python API or PokeAPI server is required for this phase.

## Setup

```bash
cd desktop_app
npm install
```

## Expected Commands After Implementation

The implementation phase must provide equivalent commands in `desktop_app/package.json`:

```bash
npm run typecheck
npm test
npm start
```

If the final command names differ, update this quickstart and `docs/architecture.md`.

## Automated Validation Scenarios

1. Typecheck passes for all app source files under `desktop_app/src/`.
2. Team Assembly renders with one active Pokemon panel and six party slots.
3. Pokemon filters update fixture-backed search results in Pokedex order.
4. Selecting a Pokemon fills the active slot and details panel.
5. Nature, item, IV points, and up to four unique moves remain attached to the selected slot after switching slots.
6. Duplicate move selection is prevented or rejected with a diagnostic.
7. IV point allocation rejects values outside 0-31 per stat and totals above 186.
8. Save action validates the team draft and adds it to saved-team state.
9. Saved Teams screen shows three teams per page and paginates at least four fixture/saved teams.
10. Missing fixture data and future contract version mismatches render diagnostics or placeholders instead of fabricated facts.
11. Fixture-backed search, slot selection, screen navigation, and saved-team pagination complete without visible delay during repeatable local validation.

## Manual Desktop Check

```bash
cd desktop_app
npm start
```

Expected result:

- The app opens in Electron without requiring a backend.
- The Team Assembly screen is the first usable screen.
- The user can build or edit a team using fixture data.
- The user can save a draft and navigate to Saved Teams.
- Saved Teams displays three teams per page and can navigate back to Team Assembly.
- IV point controls enforce 0-31 per stat and 186 total points.
- Diagnostics appear for missing fixture data and simulated service contract mismatch cases.

Validation note from implementation: `npm start` was exercised with a 12 second
timeout in the Codex environment after `npm run build`. The Electron process
stayed alive until timeout; Chromium emitted zygote warnings in this headless
environment, but no renderer build failure or fatal GPU crash occurred after the
main-process GPU switches were added.

## Out Of Scope For This Phase

- Python BFF or FastAPI routes.
- Real persistence.
- Live PokeAPI calls.
- MCP tool changes.
- Manual local PokeAPI validation.
