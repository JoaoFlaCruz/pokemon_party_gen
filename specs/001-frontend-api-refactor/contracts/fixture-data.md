# Contract: Fixture Data

Fixture data exists only to validate frontend workflows before API integration. It must be small, deterministic, source-noted, and clearly named as demo data.

## Required Fixture Sets

- Pokemon summaries: at least 6 entries, including one one-type Pokemon and one two-type Pokemon.
- Pokemon details: details for every Pokemon summary used by default screens.
- Moves: at least 8 moves, with physical, special, and status examples.
- Natures: at least 5 natures, including one neutral nature if represented.
- Items: at least 5 items, including one item with a missing image reference to test placeholder display.
- Saved teams: at least 4 saved teams to validate pagination of three teams per page.

## Rules

- Fixtures must be colocated under `desktop_app/src/renderer/data/` or equivalent TypeScript source path.
- Fixture files must export typed data structures, not raw untyped objects consumed directly by components.
- Fixtures must include a comment or naming convention that marks them as demo data for frontend validation.
- Fixtures that display factual Pokemon identity, stat, move, nature, item, or ability values must include a source note pointing to a PokeAPI-compatible snapshot or existing project fixture used to copy those values.
- Fixtures must not claim completeness, legality, competitive accuracy, or source authority.
- UI tests must be able to import or initialize the same fixture dataset.

## Diagnostics To Simulate

- Missing Pokemon details for an otherwise listed Pokemon.
- Missing item image URL.
- Attempt to save duplicate moves.
- Attempt to save an invalid IV point value.
- Future service contract version mismatch.
