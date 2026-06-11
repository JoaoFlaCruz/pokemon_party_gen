## 1. Documentation Translation

- [x] 1.1 Translate and rename `docs/arquitetura.md` to `docs/architecture.md` while preserving commands, paths, tool names, and configuration keys.
- [x] 1.2 Translate and rename `docs/padrao-agentico-times.md` to `docs/agentic-team-pattern.md` while preserving response examples, JSON keys, role names, and team-building rules.
- [x] 1.3 Translate and rename `docs/fluxo-agentico-times.md` to `docs/agentic-team-flow.md` while preserving the A-E agent responsibilities and workflow semantics.
- [x] 1.4 Update repository references to the renamed documentation paths.
- [x] 1.5 Review repository-facing docs outside `docs/` for direct references to the same team-building flow and update only relevant references.

## 2. Agentic Flow Improvement

- [x] 2.1 Add a clear 1-to-5-call decision guide to the agentic team-flow documentation.
- [x] 2.2 Document the single-call path where `build_pokemon_team` is sufficient for basic team completion.
- [x] 2.3 Document deeper validation paths using additional calls to `rank_pokemon`, `rank_pokemon_moveset`, `get_type_relations`, and `list_items`.
- [x] 2.4 Clarify that agents should stop at the lowest call count that satisfies the user request and validation needs.

## 3. Spec And Review

- [x] 3.1 Update or sync the `team-builder-tool` main spec with the new English documentation and 1-to-5-call flow requirements.
- [x] 3.2 Review translated docs against the original technical contracts to ensure behavior was not changed accidentally.
- [x] 3.3 Verify no runtime MCP schema or Python behavior changes are required.
- [x] 3.4 Run the documented unit test suite if code or tool-contract references are touched.
