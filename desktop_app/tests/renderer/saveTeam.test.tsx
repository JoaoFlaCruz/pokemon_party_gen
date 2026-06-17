import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderApp } from "./test-utils";

describe("save team", () => {
  it("saves a configured team and navigates to saved teams", async () => {
    await renderApp();
    await userEvent.click(screen.getByText(/#7 squirtle/i));
    await userEvent.click(screen.getByText(/Salvar time/i));
    expect(await screen.findByText(/Times Salvos/i)).toBeInTheDocument();
    expect(screen.getByText(/Time 1/i)).toBeInTheDocument();
  });
});
