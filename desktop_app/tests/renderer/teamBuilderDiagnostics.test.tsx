import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderApp } from "./test-utils";

describe("team builder diagnostics", () => {
  it("renders missing Pokemon details diagnostics", async () => {
    await renderApp();
    await userEvent.type(screen.getByLabelText("Nome"), "missingno");
    await userEvent.click(await screen.findByText(/missingno-demo/i));
    expect(await screen.findByText(/fixture details are unavailable/i)).toBeInTheDocument();
  });
});
