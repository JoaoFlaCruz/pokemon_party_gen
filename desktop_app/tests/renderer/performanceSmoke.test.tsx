import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderApp } from "./test-utils";

const VISIBLE_DELAY_THRESHOLD_MS = 5000;

describe("fixture interaction timing", () => {
  it("keeps local interactions under visible-delay thresholds", async () => {
    await renderApp();
    const started = performance.now();
    await userEvent.type(screen.getByLabelText("Nome"), "squirtle");
    await screen.findByText(/#7 squirtle/i);
    await userEvent.click(screen.getByText(/#7 squirtle/i));
    await screen.findByText(/Total base: 314/i);
    await userEvent.click(screen.getByText(/Times Salvos/i));
    await screen.findByText(/Pagina 1/i);
    expect(performance.now() - started).toBeLessThan(VISIBLE_DELAY_THRESHOLD_MS);
  });
});
