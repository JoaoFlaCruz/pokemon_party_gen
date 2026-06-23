import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderApp } from "./test-utils";

describe("nature and item selection", () => {
  it("assigns nature and item to the active slot", async () => {
    await renderApp();
    await userEvent.click(screen.getByText(/#1 bulbasaur/i));
    await userEvent.selectOptions(screen.getByLabelText("Natureza"), "adamant");
    await userEvent.selectOptions(screen.getByLabelText("Item"), "demo-missing-image");
    expect(screen.getByText(/Imagem indisponivel/i)).toBeInTheDocument();
  });
});
