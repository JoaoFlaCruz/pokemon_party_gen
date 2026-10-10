import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { BoxHeader } from "../../src/renderer/components/BoxHeader";
import { MoveDetailModal } from "../../src/renderer/components/MoveDetailModal";
import { PartySlotGrid } from "../../src/renderer/components/PartySlotGrid";
import { PokedexEntryBox } from "../../src/renderer/components/PokedexEntryBox";
import { StatBarChart } from "../../src/renderer/components/StatBarChart";
import { SynergySuggestions } from "../../src/renderer/components/SynergySuggestions";
import { moves, pokemonDetails, pokemonSummaries } from "../../src/renderer/data/demo-fixtures";
import type { TeamSlot } from "../../src/renderer/types/app-state";
import { emptyIvPoints } from "../../src/renderer/types/domain";

describe("PC do Bill visual components", () => {
  it("renders StatBarChart with all 6 stats and total", () => {
    const bulbasaur = pokemonDetails[0];
    render(<StatBarChart baseStats={bulbasaur.baseStats} totalStats={bulbasaur.totalStats} />);

    expect(screen.getByText("Estatísticas Base")).toBeInTheDocument();
    expect(screen.getByText("Total: 318")).toBeInTheDocument();
    expect(screen.getByText("HP")).toBeInTheDocument();
    expect(screen.getByText("Atk")).toBeInTheDocument();
    expect(screen.getByText("Def")).toBeInTheDocument();
    expect(screen.getByText("SpA")).toBeInTheDocument();
    expect(screen.getByText("SpD")).toBeInTheDocument();
    expect(screen.getByText("Spe")).toBeInTheDocument();
  });

  it("renders BoxHeader with tree decor and supports navigation", async () => {
    const onSwitch = vi.fn();
    const onNameChange = vi.fn();

    render(
      <BoxHeader
        teamName="Time 1"
        activeTeamIndex={1}
        maxTeams={10}
        onNameChange={onNameChange}
        onSwitchTeam={onSwitch}
      />
    );

    expect(screen.getByLabelText("Nome do time")).toHaveValue("Time 1");
    expect(screen.getByText("(6 PkmN)")).toBeInTheDocument();

    const prevBtn = screen.getByLabelText("Time anterior");
    expect(prevBtn).toBeDisabled();

    const nextBtn = screen.getByLabelText("Próximo time");
    expect(nextBtn).toBeEnabled();

    await userEvent.click(nextBtn);
    expect(onSwitch).toHaveBeenCalledWith(2);
  });

  it("renders PokedexEntryBox with species lore and types", () => {
    const charmander = pokemonDetails[1];
    render(<PokedexEntryBox details={charmander} />);

    expect(screen.getByText("POKEDEX")).toBeInTheDocument();
    expect(screen.getByText("No. 004")).toBeInTheDocument();
    expect(screen.getByText("charmander")).toBeInTheDocument();
    expect(screen.getByText(/strength of its life force/i)).toBeInTheDocument();
  });

  it("renders PartySlotGrid with Ace and Partner badges", () => {
    const slots: TeamSlot[] = [1, 2, 3, 4, 5, 6].map((position) => ({
      position,
      pokemonId: position === 1 ? 1 : position === 2 ? 4 : null,
      level: 100,
      gender: "male",
      natureId: null,
      itemId: null,
      ivPoints: emptyIvPoints(),
      moveIds: []
    }));

    const pokemonById = new Map(pokemonSummaries.map((p) => [p.id, p]));
    const onSelect = vi.fn();

    render(
      <PartySlotGrid
        slots={slots}
        activeSlotPosition={1}
        pokemonById={pokemonById}
        onSelect={onSelect}
      />
    );

    expect(screen.getByLabelText("Ace")).toBeInTheDocument();
    expect(screen.getByLabelText("Parceiro")).toBeInTheDocument();
    expect(screen.getByText("bulbasaur")).toBeInTheDocument();
    expect(screen.getByText("charmander")).toBeInTheDocument();
  });

  it("renders MoveDetailModal and allows closing", async () => {
    const flamethrower = moves.find((m) => m.id === "flamethrower")!;
    const onClose = vi.fn();

    render(<MoveDetailModal move={flamethrower} onClose={onClose} />);

    expect(screen.getByText("Flamethrower")).toBeInTheDocument();
    expect(screen.getByText("Fogo")).toBeInTheDocument();
    expect(screen.getByText("Especial")).toBeInTheDocument();
    expect(screen.getByText("90")).toBeInTheDocument();
    expect(screen.getByText(/intense fire/i)).toBeInTheDocument();

    const closeBtn = screen.getByLabelText("Fechar");
    await userEvent.click(closeBtn);
    expect(onClose).toHaveBeenCalled();
  });

  it("renders SynergySuggestions and handles selection", async () => {
    const bulbasaur = pokemonDetails[0];
    const onSelect = vi.fn();

    render(
      <SynergySuggestions
        activeDetails={bulbasaur}
        catalog={pokemonSummaries}
        onSelectPokemon={onSelect}
      />
    );

    expect(screen.getByText("Sugestões")).toBeInTheDocument();
    const addBtns = screen.getAllByRole("button", { name: /adicionar/i });
    expect(addBtns.length).toBeGreaterThan(0);

    await userEvent.click(addBtns[0]);
    expect(onSelect).toHaveBeenCalled();
  });
});
