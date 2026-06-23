# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Electron/Node version, or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., Electron, Python HTTP/FastAPI-compatible BFF, PokeAPI client, or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [unit, contract, integration, Electron/UI tests, manual PokeAPI checks if applicable, or NEEDS CLARIFICATION]

**Target Platform**: [e.g., desktop Electron app, local Python BFF/API, MCP stdio server, or NEEDS CLARIFICATION]

**Project Type**: [desktop-app + Python BFF/API + MCP tools, backend-only, docs-only, or NEEDS CLARIFICATION]

**Affected Layers**: [Electron UI, Python BFF/API, application use cases, infrastructure/PokeAPI adapters, MCP tools, docs, or N/A]

**Public Contracts**: [routes, MCP schemas, CLI args, JSON responses, data adapters changed, or N/A]

**Data Sources**: [local PokeAPI-compatible API, injected fakes, static fixtures, SQLite, or N/A]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Layered Architecture**: Affected layers are identified and no cross-layer bypass is introduced.
- **Contract-First Boundaries**: Route/tool/CLI/adapter input and output contracts are specified before implementation.
- **TDD Plan**: Failing tests to write first are listed, including unit tests and contract/integration tests for public boundaries.
- **Documentation Plan**: README, docs, quickstart, architecture, or team-flow updates are identified, or N/A is justified.
- **Data Fidelity**: Pokemon facts come from project tools, injected fakes, or a PokeAPI-compatible source; missing data produces diagnostics.
- **Manual Checks**: Any local PokeAPI or Electron manual validation is listed separately from automated tests.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Desktop + Python BFF/API
desktop_app/
├── main.js
├── renderer.js
├── styles.css
└── tests/

mcp_server/
├── src/
│   ├── application/
│   │   ├── api_server.py
│   │   └── use_cases/
│   ├── infrastructure/
│   │   └── pokeapi/
│   └── mcp/
└── tests/

# [REMOVE IF UNUSED] Option 3: Web application (when browser frontend + backend detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 4: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
