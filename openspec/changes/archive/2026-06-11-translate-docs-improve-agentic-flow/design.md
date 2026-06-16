## Context

The repository has user-facing and agent-facing documentation in Portuguese, while the OpenSpec capability and implementation names are in English. The current team-building flow also describes agent responsibilities, but it does not give agents a compact rule for choosing between a single `build_pokemon_team` call and a deeper validation sequence using up to five calls.

This change is primarily documentation and specification work. It should make the docs easier for agents to consume, preserve all technical contracts, and clarify the minimum useful call sequence for team generation.

## Goals / Non-Goals

**Goals:**

- Translate the project documentation under `docs/` to English.
- Rename translated Portuguese documentation files to English file names.
- Preserve commands, file paths, tool names, JSON keys, and behavioral rules while translating prose.
- Add a clear 1-to-5-call agentic flow for team building.
- Explain when each additional call is justified:
  - 1 call: `build_pokemon_team`
  - 2 calls: add candidate ranking or focused validation
  - 3 calls: add moveset validation
  - 4 calls: add type-relation auditing
  - 5 calls: add item validation or final correction
- Keep the runtime tool schema and Python behavior unchanged unless a documentation mismatch is discovered.

**Non-Goals:**

- Change the `build_pokemon_team` MCP schema.
- Rework the team-building algorithm.
- Add new tools or external dependencies.
- Translate upstream `pokeapi/` documentation.
- Rewrite generated binary diagram files.
- Rename binary diagram files unless they are explicitly referenced by translated Markdown and can be renamed without changing their contents.

## Decisions

1. Treat English as the canonical documentation language.

   The docs should use English headings, prose, and Markdown file names while retaining exact code identifiers such as `build_pokemon_team`, `rank_pokemon`, `pending`, `source=user`, and `locked=true`.

   Alternative considered: keep bilingual docs. That would reduce translation risk, but it would keep the same inconsistency that makes the agent-facing material harder to follow.

2. Rename documentation files as part of translation.

   Planned Markdown renames are:
   - `docs/arquitetura.md` -> `docs/architecture.md`
   - `docs/padrao-agentico-times.md` -> `docs/agentic-team-pattern.md`
   - `docs/fluxo-agentico-times.md` -> `docs/agentic-team-flow.md`

   All repository references to those paths should be updated in docs, OpenSpec artifacts, and agent instructions that live in this repository. The implementation should avoid renaming generated binary diagram files unless the Markdown references require it and the rename is low risk.

   Alternative considered: translate contents but keep Portuguese file names. That would leave the repository surface inconsistent and would not satisfy the request to translate file/archive names.

3. Define the 1-to-5-call flow in the team-flow docs and reference it from the team pattern docs.

   `docs/agentic-team-flow.md` is the natural home for call sequencing because it describes the agentic workflow. `docs/agentic-team-pattern.md` should include the response contract and the practical rule for choosing call depth.

   Alternative considered: put the full call sequence only in the architecture doc. The architecture doc should mention the tool contract, but detailed operational guidance belongs with the team-building docs.

4. Keep this change documentation-first.

   The current implementation already exposes `build_pokemon_team` and supporting tools. The requested improvement is about documentation and flow. Code changes should be limited to correcting mismatched presentation or references if implementation reveals a stale contract.

   Alternative considered: add an explicit `max_calls` argument to `build_pokemon_team`. That would be a behavior and schema change, and it is not necessary to document how agents should use existing tools.

## Risks / Trade-offs

- Translation may accidentally change a rule's meaning. -> Mitigate by preserving examples, JSON keys, tool names, and requirement language, and by comparing translated docs against the current docs before finalizing.
- The 1-to-5-call model could be read as mandatory for every team request. -> Mitigate by documenting it as a decision guide where 1 call is valid for simple requests and extra calls are used only when the user needs deeper validation.
- Some repository docs outside `docs/` may still contain Portuguese references or old file paths. -> Mitigate by checking repository-facing docs and updating references to renamed files.
- Binary diagram files cannot be translated safely in text form. -> Mitigate by leaving binary diagrams unchanged and documenting the English flow in Markdown.

## Migration Plan

1. Translate and rename `docs/arquitetura.md`, `docs/padrao-agentico-times.md`, and `docs/fluxo-agentico-times.md` to English file names.
2. Add the 1-to-5-call flow to the team-building docs.
3. Update related repository-facing docs if they reference the old Portuguese flow, tool descriptions, or old file paths.
4. Update the `team-builder-tool` spec with the documentation-flow requirement.
5. Run a documentation review and the existing unit test suite if code or tool-contract references are touched.

No data migration or rollback process is required. Rollback is a normal documentation revert.
