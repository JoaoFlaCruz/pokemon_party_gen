# Frontend Refactor and API Planning

Created: 2026-06-17

This document plans the desktop refactor and the local APIs that must be built before the desktop app can stop calling external Pokemon data directly. It complements `specs/001-frontend-api-refactor/spec.md`.

Current phase note: `specs/001-frontend-api-refactor/plan.md` implements only the frontend screens with source-noted demo fixtures, `contractVersion` metadata, IV point validation, and local save simulation. The HTTP APIs below are future backend contracts and are not consumed by the current frontend-only phase.

## Refactor Target

- Rebuild `desktop_app` as a modern Electron desktop app with application source written only in TypeScript.
- Replace direct browser calls to public PokeAPI URLs with local Python BFF/API calls.
- Keep the visible workflows from `docs/project/descritivo.md`: team assembly, Pokemon filtering, active Pokemon details, nature selection, item selection, four move choices, team save, and saved-team display with pagination of three teams.
- Keep Pokemon source facts traceable to a PokeAPI-compatible source through the BFF. Do not hardcode or invent Pokemon, move, nature, item, or stat facts.

## Proposed Desktop Source Layout

```text
desktop_app/
  package.json
  tsconfig.json
  src/
    main/
      main.ts
      preload.ts
    renderer/
      app.tsx
      components/
      pages/
      services/
      state/
      types/
      styles/
```

All new application code under `desktop_app/src/` should be TypeScript or TSX. Generated build output, package metadata, lockfiles, static HTML entry files, and style assets may remain non-TypeScript when required by the desktop toolchain.

## Shared API Response Envelope

All API responses should be JSON and follow a predictable envelope:

```json
{
  "data": {},
  "diagnostics": [],
  "meta": {
    "contractVersion": "1.0"
  }
}
```

Errors should use the same diagnostic shape:

```json
{
  "code": "invalid_input",
  "message": "Human-readable message",
  "field": "optional.field.path",
  "severity": "error"
}
```

## APIs To Build

### 1. List Pokemon

`GET /api/pokemon`

Purpose: provide the filtered Pokemon list used by the team assembly screen.

Query parameters:

- `typeA`: optional Pokemon type identifier.
- `typeB`: optional Pokemon type identifier.
- `name`: optional case-insensitive name fragment.
- `pokedexNumber`: optional exact Pokedex number.
- `limit`: optional page size.
- `offset`: optional page offset.

Response data:

```json
{
  "results": [
    {
      "id": 25,
      "name": "pikachu",
      "pokedexNumber": 25,
      "types": ["electric"],
      "spriteUrl": "https://..."
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

Rules:

- Sort results by `pokedexNumber` ascending.
- Return an empty list for no matches.
- Return diagnostics when the PokeAPI-compatible source is unavailable.

### 2. Get Pokemon Details

`GET /api/pokemon/{pokemonIdOrName}`

Purpose: populate the selected Pokemon details panel.

Response data:

```json
{
  "id": 25,
  "name": "pikachu",
  "pokedexNumber": 25,
  "types": ["electric"],
  "baseStats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "specialAttack": 50,
    "specialDefense": 50,
    "speed": 90
  },
  "totalStats": 320,
  "abilities": ["static", "lightning-rod"],
  "moveIds": ["thunder-shock", "quick-attack"],
  "imageUrl": "https://...",
  "spriteUrl": "https://...",
  "description": "Pokemon description"
}
```

Rules:

- `totalStats` is calculated by the BFF.
- Preserve one-type Pokemon as a single-item `types` list.
- Do not fabricate missing descriptions; return diagnostics and a null or empty display field.

### 3. List Natures

`GET /api/natures`

Purpose: populate the nature selector for a Pokemon.

Response data:

```json
{
  "results": [
    {
      "id": "adamant",
      "name": "adamant",
      "bonusStat": "attack",
      "onusStat": "specialAttack",
      "description": "Increases Attack and decreases Special Attack"
    }
  ]
}
```

Rules:

- Include neutral natures with null `bonusStat` and `onusStat` if the source represents them that way.
- Descriptions should come from source data or documented BFF mapping.

### 4. List Items

`GET /api/items`

Purpose: populate the held-item selector.

Query parameters:

- `name`: optional case-insensitive item name fragment.
- `limit`: optional page size.
- `offset`: optional page offset.

Response data:

```json
{
  "results": [
    {
      "id": "leftovers",
      "name": "leftovers",
      "description": "Item description",
      "imageUrl": "https://..."
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

Rules:

- Return only items that can reasonably be selected as held items when the source can distinguish that.
- Return diagnostics for items without image references instead of inventing image URLs.

### 5. List Pokemon Moves

`GET /api/pokemon/{pokemonIdOrName}/moves`

Purpose: populate the four move selectors for the selected Pokemon.

Response data:

```json
{
  "pokemonId": 25,
  "results": [
    {
      "id": "quick-attack",
      "name": "quick-attack",
      "type": "normal",
      "power": 40,
      "pp": 30,
      "description": "Move description",
      "damageClass": "physical"
    }
  ]
}
```

Rules:

- Include only moves available to the selected Pokemon from source data.
- `damageClass` should distinguish physical, special, and status when available.
- The frontend excludes already selected moves locally, and the save API validates duplicates.

### 6. Save Team

`POST /api/teams`

Purpose: persist a user's team from the assembly screen.

Request body:

```json
{
  "name": "Time 1",
  "slots": [
    {
      "position": 1,
      "pokemonId": 25,
      "natureId": "adamant",
      "itemId": "leftovers",
      "ivPoints": {
        "hp": 0,
        "attack": 0,
        "defense": 0,
        "specialAttack": 0,
        "specialDefense": 0,
        "speed": 0
      },
      "moveIds": ["quick-attack"]
    }
  ]
}
```

Response data:

```json
{
  "teamId": "team-001",
  "name": "Time 1",
  "savedAt": "2026-06-17T00:00:00Z"
}
```

Validation:

- Team name is required.
- Slot positions must be unique integers from 1 to 6.
- Empty slots are allowed only when represented with null Pokemon and no Pokemon-specific choices.
- A Pokemon slot may contain no more than four moves.
- A Pokemon slot may not contain duplicate moves.
- IV points must be integers from 0 to 31 per stat and no more than 186 total.

### 7. List Saved Teams

`GET /api/teams`

Purpose: support the team display screen with pagination of three teams per page.

Query parameters:

- `page`: one-based page number, default `1`.
- `pageSize`: default `3`, maximum `3` for the display screen.

Response data:

```json
{
  "results": [
    {
      "teamId": "team-001",
      "name": "Time 1",
      "slots": [
        {
          "position": 1,
          "pokemonId": 25,
          "pokemonName": "pikachu",
          "spriteUrl": "https://...",
          "natureId": "adamant",
          "itemId": "leftovers",
          "moveIds": ["quick-attack"],
          "ivPoints": {
            "hp": 0,
            "attack": 0,
            "defense": 0,
            "specialAttack": 0,
            "specialDefense": 0,
            "speed": 0
          }
        }
      ]
    }
  ],
  "page": 1,
  "pageSize": 3,
  "totalTeams": 1,
  "totalPages": 1
}
```

Rules:

- Return teams in saved ordering unless a later requirement defines sorting.
- Preserve saved user choices even if live Pokemon facts cannot be refreshed.
- Include diagnostics per team or slot when enrichment from PokeAPI-compatible data is unavailable.

### 8. Get Saved Team

`GET /api/teams/{teamId}`

Purpose: load one saved team for detail view or future editing.

Response data: same team object shape used by `GET /api/teams`, without pagination wrapper.

Rules:

- Return `not_found` diagnostics for unknown team IDs.
- Keep persisted user choices separate from refreshed Pokemon display facts.

## Implementation Dependencies

- Python BFF/API routes must be defined before the renderer service layer is completed.
- Persistence storage must exist before `POST /api/teams` and saved-team listing can pass end-to-end tests.
- PokeAPI-compatible accessors must support Pokemon lists, details, species descriptions, moves, natures, and items.
- Contract tests should cover every API above with fake data and unavailable-source diagnostics.

## Verification Plan

- Contract tests for each API request, success response, validation error, and unavailable-data diagnostic.
- Desktop service tests that assert request parameters and response mapping.
- Renderer workflow tests for Pokemon filtering, slot selection, move uniqueness, team saving, and saved-team pagination.
- Manual check against a populated local PokeAPI-compatible source remains optional and must not replace automated tests.
