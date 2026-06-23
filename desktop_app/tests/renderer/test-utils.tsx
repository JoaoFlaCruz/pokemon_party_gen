import { render, waitFor } from "@testing-library/react";
import { App } from "../../src/renderer/app";

export async function renderApp() {
  const result = render(<App />);
  await waitFor(() => result.getByText(/bulbasaur/i));
  return result;
}
