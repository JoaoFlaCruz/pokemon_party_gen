import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderApp } from "./test-utils";

describe("team builder assignment", () => {
  it("assigns selected Pokemon to the active slot and details panel", async () => {
    await renderApp();
    await userEvent.click(screen.getByLabelText("Slot 2"));
    await userEvent.click(screen.getByText(/#25 pikachu/i));
    await waitFor(() => expect(screen.getAllByText(/pikachu/i).length).toBeGreaterThan(1));
    expect(screen.getByText(/Total base: 320/i)).toBeInTheDocument();
  });
});
