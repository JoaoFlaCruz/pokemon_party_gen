import { useEffect, useMemo, useState, type Dispatch } from "react";
import { catalogService } from "../services/catalogService";
import { pokemonCatalogService } from "../services/pokemonCatalogService";
import { teamRepository } from "../services/teamRepository";
import type { AppAction } from "../state/appState";
import type { AppState } from "../types/app-state";
import type { Item, Move, Nature, PokemonDetails, PokemonFilters, PokemonSummary, StatKey } from "../types/domain";
import { ItemSelector } from "../components/ItemSelector";
import { MoveSelectorGroup } from "../components/MoveSelectorGroup";
import { NatureSelector } from "../components/NatureSelector";
import { PartySlotGrid } from "../components/PartySlotGrid";
import { PokemonDetailPanel } from "../components/PokemonDetailPanel";
import { PokemonSearchPanel } from "../components/PokemonSearchPanel";
import { SaveTeamControls } from "../components/SaveTeamControls";
import { StatPointControls } from "../components/StatPointControls";

type Props = {
  state: AppState;
  dispatch: Dispatch<AppAction>;
};

export function TeamBuilderPage({ state, dispatch }: Props) {
  const [filters, setFilters] = useState<PokemonFilters>({});
  const [pokemonList, setPokemonList] = useState<PokemonSummary[]>([]);
  const [activeDetails, setActiveDetails] = useState<PokemonDetails | null>(null);
  const [availableMoves, setAvailableMoves] = useState<Move[]>([]);
  const [natures, setNatures] = useState<Nature[]>([]);
  const [items, setItems] = useState<Item[]>([]);

  const activeSlot = state.draft.slots.find((slot) => slot.position === state.activeSlotPosition) ?? state.draft.slots[0];

  useEffect(() => {
    pokemonCatalogService.listPokemon(filters).then((result) => {
      setPokemonList(result.data);
      dispatch({ type: "setDiagnostics", diagnostics: result.diagnostics });
    });
  }, [filters, dispatch]);

  useEffect(() => {
    catalogService.listNatures().then((result) => setNatures(result.data));
    catalogService.listItems().then((result) => setItems(result.data));
  }, []);

  useEffect(() => {
    if (!activeSlot.pokemonId) {
      setActiveDetails(null);
      setAvailableMoves([]);
      return;
    }
    pokemonCatalogService.getPokemonDetails(activeSlot.pokemonId).then((result) => {
      setActiveDetails(result.data);
      if (result.diagnostics.length) dispatch({ type: "setDiagnostics", diagnostics: result.diagnostics });
    });
    pokemonCatalogService.listMovesForPokemon(activeSlot.pokemonId).then((result) => setAvailableMoves(result.data));
  }, [activeSlot.pokemonId, dispatch]);

  const allTypes = useMemo(
    () => Array.from(new Set(pokemonList.flatMap((pokemon) => pokemon.types))).sort(),
    [pokemonList]
  );
  const pokemonById = useMemo(() => new Map(pokemonList.map((pokemon) => [pokemon.id, pokemon])), [pokemonList]);

  async function handleSave() {
    const result = await teamRepository.saveTeam(state.draft);
    if (result.diagnostics.length) {
      dispatch({ type: "setDiagnostics", diagnostics: result.diagnostics });
      return;
    }
    dispatch({ type: "saveTeam", team: result.data });
    dispatch({ type: "navigate", view: "saved-teams" });
  }

  return (
    <main className="team-builder">
      <PokemonDetailPanel details={activeDetails} slot={activeSlot} moves={availableMoves} />
      <section className="builder-center">
        <div className="team-header">
          <label>
            Nome do time
            <input value={state.draft.name} onChange={(event) => dispatch({ type: "setTeamName", name: event.target.value })} />
          </label>
          <SaveTeamControls onSave={handleSave} />
        </div>
        <PartySlotGrid
          slots={state.draft.slots}
          activeSlotPosition={state.activeSlotPosition}
          pokemonById={pokemonById}
          onSelect={(position) => dispatch({ type: "selectSlot", position })}
        />
        <section className="customization">
          <NatureSelector natures={natures} value={activeSlot.natureId} onChange={(natureId) => dispatch({ type: "setNature", natureId })} />
          <ItemSelector items={items} value={activeSlot.itemId} onChange={(itemId) => dispatch({ type: "setItem", itemId })} />
          <StatPointControls ivPoints={activeSlot.ivPoints} onChange={(stat: StatKey, value) => dispatch({ type: "setIv", stat, value })} />
          <MoveSelectorGroup availableMoves={availableMoves} selectedMoveIds={activeSlot.moveIds} onMoveChange={(index, moveId) => dispatch({ type: "setMove", index, moveId })} />
        </section>
      </section>
      <PokemonSearchPanel
        filters={filters}
        results={pokemonList}
        types={allTypes}
        onFiltersChange={setFilters}
        onSelectPokemon={(pokemonId) => dispatch({ type: "assignPokemon", pokemonId })}
      />
    </main>
  );
}
