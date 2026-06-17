<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles:
- Template principle 1 -> I. Layered Product Architecture
- Template principle 2 -> II. Contract-First API Boundaries
- Template principle 3 -> III. Test-Driven Delivery
- Template principle 4 -> IV. Documentation Is a Deliverable
- Template principle 5 -> V. Data Fidelity and Traceability
Added sections:
- Product Architecture Constraints
- Development Workflow and Quality Gates
Removed sections:
- None
Templates requiring updates:
- Updated: .specify/templates/plan-template.md
- Updated: .specify/templates/spec-template.md
- Updated: .specify/templates/tasks-template.md
- Reviewed: .specify/templates/commands/*.md (no command templates present)
Runtime guidance requiring updates:
- Updated: README.md
- Updated: docs/architecture.md
- Reviewed: AGENTS.md (no change required)
Follow-up TODOs:
- None
-->
# Pokemon Party Gen Constitution

## Core Principles

### I. Layered Product Architecture
Pokemon Party Gen MUST preserve a layered architecture with explicit ownership
boundaries: Electron owns the desktop user interface, the Python BFF/API layer
owns application orchestration and HTTP contracts, domain and use-case modules own
business rules, infrastructure modules own external API and persistence access,
and PokeAPI-compatible services own Pokemon source data. Code MUST NOT bypass
these boundaries; cross-layer calls require a documented contract and tests.

Rationale: the project combines desktop UX, Python services, MCP tools, and
Pokemon data sources. Clear boundaries keep feature work testable and prevent UI,
API, and data-access behavior from becoming coupled.

### II. Contract-First API Boundaries
Every public boundary MUST define stable, JSON-serializable contracts before
implementation. This includes Electron-to-BFF routes, BFF or FastAPI-compatible
HTTP endpoints, MCP tools, CLI entry points, and PokeAPI adapters. Input
validation, error shapes, diagnostics, and response fields MUST be specified and
covered by contract or wrapper tests when changed.

Rationale: multiple clients and agents consume the same behavior. Contract-first
changes reduce regressions and make API compatibility observable in tests.

### III. Test-Driven Delivery
All behavior changes MUST follow TDD: write or update failing tests first, confirm
the failure is meaningful, implement the smallest change that passes, then
refactor while preserving passing tests. Unit tests MUST cover pure business
rules and adapters with fakes; contract or integration tests MUST cover changed
public boundaries. Manual PokeAPI checks MAY supplement but MUST NOT replace
automated tests.

Rationale: ranking, team-building, and data adaptation are rule-heavy. Tests are
the executable proof that behavior is intentional and repeatable.

### IV. Documentation Is a Deliverable
Every implementation or behavior change MUST update the documentation that a
future maintainer or agent needs to understand it. Architecture, contracts,
environment variables, run commands, test commands, team-building rules, and data
flow changes MUST be documented in the relevant README, docs, or Spec Kit
artifact before the change is complete.

Rationale: this project is used by humans and coding agents. Documentation is
part of the operating surface, not a postscript.

### V. Data Fidelity and Traceability
Pokemon facts MUST come from project tools, injected test fakes, or a configured
PokeAPI-compatible source. The project MUST NOT fabricate Pokemon identity,
stats, moves, abilities, items, legality, or membership data. When data is
missing, incomplete, or unavailable, features MUST return explicit diagnostics or
pending states instead of invented results.

Rationale: reliable team generation depends on traceable source data. Fabricated
facts produce teams that cannot be validated.

## Product Architecture Constraints

Pokemon Party Gen is a desktop product with a multi-layer backend surface:

- Electron desktop code lives under `desktop_app/` and consumes documented local
  HTTP contracts.
- Python BFF/API code lives under `mcp_server/src/application/` or a documented
  API package and exposes FastAPI-compatible JSON behavior where an HTTP API is
  required. Transitional non-FastAPI servers MUST be documented with their route
  contracts and migration constraints.
- Business rules live under `mcp_server/src/application/use_cases/` and remain
  independently testable without real HTTP.
- External Pokemon API access and response adaptation live under
  `mcp_server/src/infrastructure/pokeapi/`.
- MCP tool schemas, validation, presentation, dispatch, and tests live under
  `mcp_server/src/mcp/tools/` and `mcp_server/src/mcp/server.py`.
- PokeAPI source/runtime code remains isolated under `pokeapi/`; project code
  consumes it through configured API contracts rather than internal imports.

New dependencies, new layers, or boundary changes require an updated architecture
document and a constitution check in the implementation plan.

## Development Workflow and Quality Gates

Feature work MUST proceed through specification, plan, tests, implementation,
documentation, and verification. A plan MUST identify affected layers, changed
contracts, data sources, and test strategy before implementation starts.

Before a change is complete:

- Automated tests covering the changed behavior MUST pass.
- New public routes, tools, or adapters MUST include contract or wrapper tests.
- Fetcher and PokeAPI adapter changes MUST use fakes or injected fetchers for
  automated coverage; real PokeAPI checks remain manual.
- Documentation changes MUST be included or explicitly justified as unnecessary.
- Any inability to validate local PokeAPI data MUST be reported as a residual
  risk rather than hidden.

## Governance

This constitution supersedes conflicting local practices and templates. Pull
requests, plans, and task lists MUST include a constitution check covering the
five core principles and the architecture constraints above. Exceptions require a
documented violation entry with reason, simpler alternative rejected, and follow-up
mitigation.

Amendments require updating this file, adding a Sync Impact Report, propagating
changes to affected Spec Kit templates and runtime guidance, and recording the
semantic version impact:

- MAJOR for removing or redefining a principle in a backward-incompatible way.
- MINOR for adding a principle, section, or materially expanded governance.
- PATCH for clarifications that do not change required behavior.

Compliance review is mandatory before merging implementation work. Reviewers and
agents MUST verify tests, documentation, contracts, and data-source traceability
against this constitution.

**Version**: 1.0.0 | **Ratified**: 2026-06-17 | **Last Amended**: 2026-06-17
