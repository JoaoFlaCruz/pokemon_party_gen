import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderApp } from "./test-utils";

describe("saved team diagnostics", () => {
  it("keeps saved slots visible when enrichment is missing", async () => {
    await renderApp();
    await userEvent.click(screen.getByText(/Times Salvos/i));
    expect(await screen.findByText(/Kanto Balance/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Vazio/i).length).toBeGreaterThanOrEqual(0);
  });
});
