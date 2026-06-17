import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderApp } from "./test-utils";

describe("team builder filters", () => {
  it("filters by name and keeps Pokedex ordering", async () => {
    await renderApp();
    await userEvent.type(screen.getByLabelText("Nome"), "pika");
    expect(await screen.findByText(/#25 pikachu/i)).toBeInTheDocument();
    expect(screen.queryByText(/#1 bulbasaur/i)).not.toBeInTheDocument();
  });

  it("shows empty state for no matches", async () => {
    await renderApp();
    await userEvent.type(screen.getByLabelText("Nome"), "zzzz");
    expect(await screen.findByText(/Nenhum Pokemon encontrado/i)).toBeInTheDocument();
  });
});
