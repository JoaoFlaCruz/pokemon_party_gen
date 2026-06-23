# Contract: Frontend Fixture Services

These contracts define TypeScript-facing service interfaces for the frontend-only phase. Implementations must use local fixtures now and may later be replaced with HTTP-backed services.

## Shared Result Shape

```ts
type DiagnosticSeverity = "info" | "warning" | "error";

type Diagnostic = {
  code: string;
  message: string;
  field?: string;
  severity: DiagnosticSeverity;
};

type ServiceResult<T> = {
  data: T;
  diagnostics: Diagnostic[];
  meta: {
    contractVersion: "fixture-1";
  };
};
```

## PokemonCatalogService

```ts
type PokemonFilters = {
  typeA?: string;
  typeB?: string;
  name?: string;
  pokedexNumber?: number;
};

interface PokemonCatalogService {
  listPokemon(filters: PokemonFilters): Promise<ServiceResult<PokemonSummary[]>>;
  getPokemonDetails(pokemonId: number): Promise<ServiceResult<PokemonDetails | null>>;
  listMovesForPokemon(pokemonId: number): Promise<ServiceResult<Move[]>>;
}
```

Rules:

- `listPokemon` returns results sorted by Pokedex number.
- `getPokemonDetails` returns `null` plus diagnostics for missing fixture entries.
- `listMovesForPokemon` returns only moves available to the selected Pokemon.

## CatalogService

```ts
interface CatalogService {
  listNatures(): Promise<ServiceResult<Nature[]>>;
  listItems(query?: string): Promise<ServiceResult<Item[]>>;
}
```

Rules:

- Nature and item selectors must render with fixture data without network access.
- Item search is optional but should be case-insensitive when present.

## TeamRepository

```ts
type TeamListPage = {
  results: SavedTeam[];
  page: number;
  pageSize: 3;
  totalTeams: number;
  totalPages: number;
};

interface TeamRepository {
  saveTeam(team: TeamDraft): Promise<ServiceResult<SavedTeam>>;
  listSavedTeams(page: number): Promise<ServiceResult<TeamListPage>>;
  getSavedTeam(teamId: string): Promise<ServiceResult<SavedTeam | null>>;
}
```

Rules:

- `saveTeam` validates team name, six slot positions, move uniqueness, and IV point limits.
- `listSavedTeams` always returns page size 3 for the Saved Teams screen.
- Saved fixture data may reset when the desktop app reloads unless implementation tasks explicitly add browser-local persistence.
- Services return a `contractVersion` metadata value and diagnostics when saved data or simulated future data uses an incompatible version.
