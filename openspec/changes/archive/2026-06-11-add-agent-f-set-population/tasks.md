## 1. Agentic Flow Documentation

- [x] 1.1 Update `docs/agentic-team-flow.md` to define Agent F as the Set Populator.
- [x] 1.2 Insert Agent F into the workflow after stable team validation and before final response.
- [x] 1.3 Document that Agent F reruns after refinements that change Pokemon, roles, trio strategy, or priority gaps.
- [x] 1.4 Document that Agent F routes missing data needs through Agent A or records unresolved set details in `pending`.
- [x] 1.5 Update completion conditions so final teams require Agent F-populated detailed sets when enough validated data and confidence are available.

## 2. Response Pattern Documentation

- [x] 2.1 Update `docs/agentic-team-pattern.md` so each final Pokemon entry includes `Nome`, `role`, `Motivo`, `Golpes`, `EVs`, `Natureza`, `Item`, and `Sugestao`.
- [x] 2.2 Update JSON examples in `docs/agentic-team-pattern.md` with structured `moves`, `evs`, `nature`, `item`, and `usage_suggestion` fields.
- [x] 2.3 Add guidance that Agent F must not invent moves, EVs, natures, or items and must use `pending` for unsupported details.

## 3. Skill Alignment

- [x] 3.1 Update `.codex/skills/create-single-team/SKILL.md` to reference `docs/agentic-team-flow.md` and `docs/agentic-team-pattern.md` instead of stale Portuguese document names.
- [x] 3.2 Add Agent F to the `create-single-team` agentic flow after validation/audit and before final output.
- [x] 3.3 Update the `create-single-team` response template so each Pokemon includes the required detailed fields.
- [x] 3.4 Ensure the skill states that `build_pokemon_team` is inactive and must not be used for team construction.

## 4. Architecture and Spec Sync

- [x] 4.1 Update `docs/architecture.md` agent overview to include Agent F and its responsibility.
- [x] 4.2 Add or sync the `agentic-team-assembly` spec into `openspec/specs/` during implementation or spec sync.
- [x] 4.3 Review the existing `team-builder-tool` spec references and avoid adding new Agent F requirements to the inactive MCP tool contract.

## 5. Verification

- [x] 5.1 Run `rg "build_pokemon_team|Agent F|create-single-team|fluxo-agentico|fluxograma_agentico" docs .codex/skills openspec/specs` and confirm references are intentional.
- [x] 5.2 Run `python3 -m unittest mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers`.
- [x] 5.3 Run `openspec status --change "add-agent-f-set-population"` and confirm all artifacts are complete.
