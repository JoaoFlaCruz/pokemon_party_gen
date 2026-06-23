# Contract: UI Workflows

## Screen: Team Assembly

Required regions:

- Active Pokemon detail panel.
- Six-slot party grid.
- Pokemon search/filter area.
- Nature selector.
- Item selector.
- Four move selectors.
- IV point controls.
- Save team command.
- Navigation to Saved Teams screen.

Required interactions:

1. Selecting a party slot updates the active details panel.
2. Typing a name or Pokedex number filter refreshes the Pokemon list from fixture service data.
3. Changing type filters refreshes the Pokemon list from fixture service data.
4. Selecting a Pokemon assigns it to the active slot and loads fixture details.
5. Selecting a nature, item, IV points, or moves updates only the active slot.
6. Selecting a move removes that move from other move selectors for the same Pokemon.
7. Saving validates the draft and adds it to the fixture-backed saved team list.

Empty states:

- Empty active slot shows a neutral details panel.
- No Pokemon filter matches show an empty-results message.
- Missing fixture details show diagnostics instead of invented data.

## Screen: Saved Teams

Required regions:

- List of saved teams.
- Six-slot summary per team.
- Pagination controls.
- Navigation back to Team Assembly.

Required interactions:

1. Opening the screen shows saved teams with three teams per page.
2. Pagination moves between pages without changing saved team content.
3. Each team displays name and six ordered slots.
4. Empty team slots remain visibly empty.
5. Saved user choices remain visible when Pokemon enrichment data is missing.

Empty states:

- No saved teams shows a clear empty-state message and a command to return to Team Assembly.

## Acceptance Mapping

- Team Assembly covers FR-001 through FR-011 and FR-017.
- Save action covers the frontend part of FR-012 and FR-014.
- Saved Teams covers FR-013 and FR-014.
- Fixture diagnostics cover the frontend behavior of FR-015.
