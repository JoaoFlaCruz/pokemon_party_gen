import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderApp } from "./test-utils";

describe("saved team pagination", () => {
  it("shows three saved teams per page and navigates pages", async () => {
    await renderApp();
    await userEvent.click(screen.getByText(/Times Salvos/i));
    expect(await screen.findByText(/Pagina 1 de/i)).toBeInTheDocument();
    expect(screen.getAllByRole("article")).toHaveLength(3);
    await userEvent.click(screen.getByText(/Proxima/i));
    expect(await screen.findByText(/Pagina 2 de/i)).toBeInTheDocument();
  });
});
