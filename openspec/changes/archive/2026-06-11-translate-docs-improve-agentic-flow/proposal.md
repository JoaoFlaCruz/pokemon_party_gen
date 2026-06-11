## Why

The project documentation is currently mixed across Portuguese and English, which makes the MCP contracts and team-building rules harder to consume consistently by agents. The team-building flow also needs a clearer operating model for 1 to 5 tool calls so agents can choose an appropriate depth of validation without over-calling tools for simple requests.

## What Changes

- Translate project documentation to English while preserving existing technical meaning, examples, commands, and file references.
- Rename Portuguese documentation file names to English equivalents and update all repository references to those paths.
- Improve the agentic team-building flow documentation with an explicit 1-to-5-call progression.
- Clarify when a single `build_pokemon_team` call is enough and when additional calls to ranking, moveset, item, or type-relation tools are expected.
- Update the `team-builder-tool` spec to require documentation of the 1-to-5-call flow as part of the tool contract.
- Keep code behavior unchanged unless implementation reveals documentation-only references that must be aligned.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `team-builder-tool`: Add requirements for English documentation and a documented 1-to-5-call agentic flow around `build_pokemon_team` and supporting tools.

## Impact

- Affected docs:
  - `docs/arquitetura.md` -> `docs/architecture.md`
  - `docs/padrao-agentico-times.md` -> `docs/agentic-team-pattern.md`
  - `docs/fluxo-agentico-times.md` -> `docs/agentic-team-flow.md`
  - repository-facing docs if they contain references to the same team-building flow
- Affected specs:
  - `openspec/specs/team-builder-tool/spec.md`
- No API, schema, external dependency, or database changes are expected.
