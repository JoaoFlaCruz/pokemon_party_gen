## 1. Workflow Documentation

- [x] 1.1 Update `docs/agentic-team-flow.md` with explicit reflection checkpoints after initial build, validation, audit, and before final response.
- [x] 1.2 Add the `accept`, `refine`, `ask_user`, and `stop_with_pending` reflection decision vocabulary to `docs/agentic-team-flow.md`.
- [x] 1.3 Document loop-control rules in `docs/agentic-team-flow.md` so agents stop at the lowest sufficient call count and only refine the highest-priority actionable gap.
- [x] 1.4 Update `docs/agentic-team-pattern.md` with concise final-response and reflection guidance for Pokemon team creation.

## 2. Spec And Consistency

- [x] 2.1 Sync the new reflection requirements into `openspec/specs/team-builder-tool/spec.md` during apply or sync.
- [x] 2.2 Review `README.md`, `AGENTS.md`, `CODEX.md`, and `docs/architecture.md` references for consistency with the improved reflection workflow.
- [x] 2.3 Confirm no MCP schema or runtime code changes are required; if implementation reveals a contract change, add focused tool tests and update architecture docs.

## 3. Verification

- [x] 3.1 Run `openspec status --change "improve-team-reflection-pattern"` and confirm the change is apply-ready.
- [x] 3.2 If code or tool contracts change, run `python3 -m unittest mcp_server.tests.application.use_cases.test_rankings mcp_server.tests.mcp.tools.test_tools mcp_server.tests.infrastructure.pokeapi.test_fetchers`.
