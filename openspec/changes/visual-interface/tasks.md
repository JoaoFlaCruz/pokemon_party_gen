## 1. Backend Bridge API Setup

- [x] 1.1 Create the `mcp_server/src/application/api_server.py` file with a standard library `http.server` implementation.
- [x] 1.2 Implement JSON parsing, request dispatching, and error handling.
- [x] 1.3 Add CORS headers support for all responses (Origin, Methods, Headers).
- [x] 1.4 Add the `/api/build-team` endpoint that delegates to `build_pokemon_team`.
- [x] 1.5 Add helper endpoints like `/api/rankings`, `/api/moves`, and `/api/types` to expose other MCP use cases.
- [x] 1.6 Verify backend server runs locally using a simple Python script or terminal command.

## 2. Electron Desktop App Setup

- [x] 2.1 Initialize an Electron project in a new directory at the root named `desktop_app`.
- [x] 2.2 Configure `package.json` with dependencies (`electron`) and scripts (`npm run start`).
- [x] 2.3 Create `main.js` to initialize the Electron window and load `index.html`.
- [x] 2.4 Create `styles.css` with a custom CSS design system using HSL color variables (dark cyberpunk theme, glassmorphism, responsive grids, Outfit font).

## 3. Desktop UI Component Implementation

- [x] 3.1 Build the Search and Autocomplete view to search Pokemon from the API.
- [x] 3.2 Implement team selection logic (up to 6 members, toggle locked state, select up to 2 aces).
- [x] 3.3 Design the Team Layout view displaying primary and complementary trios as separate sections, highlighting aces with custom styles.
- [x] 3.4 Implement a Pokemon Detail card/modal that shows stats, inferred roles, and movesets/rankings.
- [x] 3.5 Build the Team Analysis view showing the type relation matrix (weaknesses/resistances) and team-level strengths/risks.

## 4. Integration & Documentation

- [x] 4.1 Connect Electron view scripts to fetch from the local API bridge server.
- [x] 4.2 Test the full desktop app flow end-to-end (selection -> generation -> analysis -> movesets).
- [x] 4.3 Update `README.md` and `docs/architecture.md` with instructions on running the API server and the Electron desktop app.
