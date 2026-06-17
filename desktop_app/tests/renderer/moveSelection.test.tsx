import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderApp } from "./test-utils";

describe("move selection", () => {
  it("prevents duplicate moves and shows move descriptions", async () => {
    await renderApp();
    await userEvent.click(screen.getByText(/#25 pikachu/i));
    await userEvent.selectOptions(screen.getByLabelText("Golpe 1"), "quick-attack");
    expect(screen.getByText(/blinding speed/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Golpe 2")).not.toHaveTextContent("Quick Attack");
  });
});
