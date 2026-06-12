## Context

The Pokemon Party Generator currently exposes all its team-building and ranking logic via Python CLI commands and an MCP stdio server. There is no graphical user interface to allow interactive team creation, slot-by-slot team building, or visual auditing of team strengths and type relationships.

To address this, we will design an Electron desktop application supported by a lightweight Python HTTP server that exposes the existing use cases as REST endpoints.

## Goals / Non-Goals

**Goals:**
- Create a desktop application using Electron, HTML, CSS, and Vanilla JavaScript.
- Implement a premium visual design with dark mode, glowing accents, glassmorphic styling, and responsive grids suited for a desktop app.
- Expose a local Python HTTP API server (using Python's standard library `http.server` to avoid new external dependencies) that serves as a bridge between the Electron application and the Python use case logic (`build_pokemon_team`, `rank_pokemon`, `rank_pokemon_moveset`).
- Allow users to select Pokemon, assign aces, view primary/complementary trios, inspect type coverage, and see move recommendations inside the desktop app.

**Non-Goals:**
- Creating installers/packages for all operating systems (running with `npm start` is sufficient for development/local use).
- Replacing or breaking the existing stdio-based MCP server.
- Adding complex frontend libraries (React/Vue/Angular); using simple Vanilla JS or React within Electron is fine, but for lightweight performance, standard ES6 modules or a simple React/Vite/Electron structure works. We will use a standard Electron boilerplate or plain HTML/JS for simplicity and maximum predictability.

## Decisions

### Decision 1: UI Shell and Desktop Wrapper
- **Choice**: Electron
- **Rationale**: Electron is the industry-standard desktop application framework. It allows building cross-platform desktop interfaces using web technologies.
- **Alternatives Considered**: Web browsers (the user specifically requested a desktop app platform).

### Decision 2: Backend Communication Bridge
- **Choice**: A lightweight Python HTTP server using built-in `http.server` and `json` modules.
- **Rationale**: Since the existing code runs as an MCP stdio server, standard web/desktop applications cannot communicate with it directly without a bridge. Running a simple HTTP daemon on `http://127.0.0.1:8002` written in pure Python requires zero new pip packages, avoiding potential dependency hell.
- **Alternatives Considered**: Direct Python integration via child process/node-py (more brittle than simple HTTP REST communication).

### Decision 3: Styling Strategy
- **Choice**: Vanilla CSS with custom variables.
- **Rationale**: Adheres to the technology guidelines. Allows creation of gorgeous glassmorphism cards and smooth desktop animations without external build tooling dependencies.

## Risks / Trade-offs

- **[Risk] CORS / Network connectivity** → *Mitigation*: The Python server runs locally on `http://127.0.0.1:8002`, and Electron can communicate with it directly, bypassing CORS issues since Electron's main/renderer processes can fetch arbitrary local hosts or run with disabled web security if needed.
- **[Risk] PokeAPI local container** → *Mitigation*: The backend Python HTTP server handles connectivity errors and reports them gracefully in the `pending` list of the response.
- **[Risk] NPM/Node.js setup on host** → *Mitigation*: The user will run the Electron app via `npm run start` or similar local commands.
