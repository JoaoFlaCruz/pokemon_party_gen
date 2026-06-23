import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderApp } from "./test-utils";

describe("IV point allocation", () => {
  it("rejects invalid IV values and persists valid slot values", async () => {
    await renderApp();
    await userEvent.click(screen.getByText(/#4 charmander/i));
    const attackInput = screen.getByLabelText("IV attack");
    await userEvent.clear(attackInput);
    await userEvent.type(attackInput, "31");
    expect(attackInput).toHaveValue(31);
    await userEvent.clear(attackInput);
    await userEvent.type(attackInput, "32");
    expect(await screen.findByText(/0 to 31/i)).toBeInTheDocument();
  });
});
