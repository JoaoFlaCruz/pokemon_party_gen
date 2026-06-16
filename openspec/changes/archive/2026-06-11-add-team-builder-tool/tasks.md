## 1. Core Use Case

- [x] 1.1 Add a team-building use case module under `mcp_server/src/application/use_cases/`.
- [x] 1.2 Define JSON-serializable output structures for team members, team structure, analysis, and pending issues.
- [x] 1.3 Implement input normalization for user-selected Pokemon, duplicate handling, and six-Pokemon limit handling.
- [x] 1.4 Implement validation of user-selected Pokemon through injected data providers without inventing missing data.
- [x] 1.5 Implement deterministic candidate selection for open slots using existing ranking data or injected ranker fakes.
- [x] 1.6 Assign team members into primary and complementary trios with ace, role, reason, and gap-coverage metadata.
- [x] 1.7 Add pending issue generation for unresolved Pokemon, insufficient candidates, data-source failures, and conflicting constraints.

## 2. MCP Tool

- [x] 2.1 Add `mcp_server/src/mcp/tools/team_builder_tool.py` with tool schema, argument validation, executor, and presentation formatting.
- [x] 2.2 Register `build_pokemon_team` in `mcp_server/src/mcp/server.py` tool imports, tool map, and initialize instructions.
- [x] 2.3 Export or import the new tool consistently with existing MCP tool module patterns.
- [x] 2.4 Ensure MCP `tools/call` returns presentation text and structured content for `build_pokemon_team`.

## 3. Tests

- [x] 3.1 Add use-case tests with fake providers for minimal request completion, user-selected Pokemon preservation, duplicate handling, and six-Pokemon limit handling.
- [x] 3.2 Add use-case tests for unknown Pokemon, unavailable data, insufficient candidates, trio assignment, and AI-selected member explanations.
- [x] 3.3 Add MCP tool tests for schema shape, argument validation, presentation formatting, and structured response shape.
- [x] 3.4 Add MCP server dispatch tests showing `build_pokemon_team` appears in `tools/list` and works through `tools/call`.
- [x] 3.5 Run the repository unit test command documented in `docs/architecture.md`.

## 4. Documentation

- [x] 4.1 Update `docs/architecture.md` with the new use case, MCP tool, input/output contract, dispatch registration, and tests.
- [x] 4.2 Update `docs/agentic-team-pattern.md` with the executable tool contract and any response-format refinements.
- [x] 4.3 Update `docs/agentic-team-flow.md` to explain how the tool maps the A-E flow into deterministic orchestration.
- [x] 4.4 Document any intentionally deferred scope such as held item suggestions, moveset finalization, or controlled randomness.
