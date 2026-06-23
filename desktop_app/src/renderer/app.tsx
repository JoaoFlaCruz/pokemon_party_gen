import { useReducer } from "react";
import { AppShell } from "./components/AppShell";
import { SavedTeamsPage } from "./pages/SavedTeamsPage";
import { TeamBuilderPage } from "./pages/TeamBuilderPage";
import { appReducer, createInitialState } from "./state/appState";

export function App() {
  const [state, dispatch] = useReducer(appReducer, undefined, createInitialState);

  return (
    <AppShell currentView={state.currentView} diagnostics={state.diagnostics} onNavigate={(view) => dispatch({ type: "navigate", view })}>
      {state.currentView === "team-builder" ? <TeamBuilderPage state={state} dispatch={dispatch} /> : <SavedTeamsPage state={state} dispatch={dispatch} />}
    </AppShell>
  );
}
