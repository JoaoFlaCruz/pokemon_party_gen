import { describe, expect, it } from "vitest";
import { appReducer, createInitialState } from "../../src/renderer/state/appState";

describe("app state reducer", () => {
  it("navigates, selects slots, and assigns Pokemon", () => {
    let state = createInitialState();
    state = appReducer(state, { type: "navigate", view: "saved-teams" });
    expect(state.currentView).toBe("saved-teams");
    state = appReducer(state, { type: "selectSlot", position: 3 });
    state = appReducer(state, { type: "assignPokemon", pokemonId: 25 });
    expect(state.draft.slots[2].pokemonId).toBe(25);
  });

  it("rejects invalid IV values and duplicate moves", () => {
    let state = createInitialState();
    state = appReducer(state, { type: "assignPokemon", pokemonId: 25 });
    state = appReducer(state, { type: "setIv", stat: "attack", value: 32 });
    expect(state.diagnostics[0].code).toBe("invalid_iv_value");
    state = appReducer(state, { type: "setMove", index: 0, moveId: "quick-attack" });
    state = appReducer(state, { type: "setMove", index: 1, moveId: "quick-attack" });
    expect(state.diagnostics[0].code).toBe("duplicate_moves");
  });
});
