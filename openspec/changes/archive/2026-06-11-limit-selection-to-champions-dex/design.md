## Context

The current ranking path asks `PokemonFetcher` for all Pokemon or for intersections of type, ability, and move filters. `rank_pokemon` scores that pool, and `build_pokemon_team` uses the same ranking path to fill any slots not locked by the user.

The bundled PokeAPI-compatible source already models Pokemon Champions as a Pokédex: `pokeapi/data/v2/csv/pokedexes.csv` contains id `36` with identifier `champions`, `pokedex_prose.csv` names it "Champions dex", and `pokedex_version_groups.csv` links it to the `champions` version group. The OpenAPI contract exposes `/api/v2/pokedex/{id}/` with string or integer ids and returns `pokemon_entries[].pokemon_species.name`, which is the stable source for library membership.

## Goals / Non-Goals

**Goals:**

- Limit AI candidate selection to Pokemon species present in the Champions Pokédex.
- Keep user-selected Pokemon fixed after normal validation, while making out-of-library status explicit in `pending` and member metadata.
- Reuse the existing PokeAPI-compatible REST client pattern and avoid static Pokemon lists.
- Keep ranking deterministic after the Champions filter is applied.
- Document the source endpoint and output metadata.

**Non-Goals:**

- Do not invent or maintain a local hard-coded Champions Pokemon list.
- Do not change ranking score weights, role inference, banned-Pokemon filtering, or team trio rules except where needed to report Champions scope.
- Do not require the local PokeAPI server during unit tests; tests should use fakes or injected fetchers.

## Decisions

1. Add Champions membership discovery to the PokeAPI infrastructure layer.

   The fetcher will retrieve `pokedex/champions/` and read `pokemon_entries[].pokemon_species.name`. If an API implementation does not resolve the string identifier but has the bundled numeric id, it can retry `pokedex/36/`. This keeps the code aligned with the documented API and CSV data without duplicating data.

   Alternative considered: filter by `version-group/champions`. That relationship identifies the game/version group, but Pokédex membership is the direct library contract and already exposes the species list.

2. Filter candidate names before fetching individual Pokemon summaries.

   `PokemonFetcher._candidate_names()` already creates a name set from all Pokemon or from filters. The Champions filter should intersect this set with species membership before expensive detail fetches. Because Pokédex entries are species-level while `/pokemon/` returns forms, the implementation should include Pokemon whose `species.name` is in the Champions set. For plain default forms this usually matches the Pokemon name; form-specific behavior must be validated by fetching summaries or by mapping species names conservatively.

   Alternative considered: fetch all Pokemon summaries and filter by `species.name` afterward. That is simpler but wastes many HTTP calls and makes team generation slower.

3. Make Champions scope the default for AI selection and ranking tool execution.

   The team builder's default candidate ranker should call ranking with Champions scope enabled. The ranking tool should report the selected library scope so callers can verify that results came from the intended pool. If a future caller needs an unrestricted internal ranker for diagnostics, that should be an explicit argument or helper rather than the default MCP behavior.

   Alternative considered: only filter inside the team builder. That would leave the ranking tool able to recommend non-Champions candidates, creating inconsistent AI behavior.

4. Preserve user-selected Pokemon while recording out-of-library status.

   User choices are fixed members by existing contract. The change should not silently remove a valid user-selected Pokemon just because it is outside Champions. Instead, the output should retain the member as `source=user`, `locked=true`, and record a `pending` issue such as `user-pokemon-outside-champions-dex`.

   Alternative considered: reject out-of-library user choices. That conflicts with the existing preservation rule and would make mixed user constraints harder to resolve.

## Risks / Trade-offs

- [Risk] PokeAPI-compatible servers may not include the latest Champions dex or may not resolve `champions` as an id. -> Mitigation: use the documented string id first, retry numeric id `36`, and surface data failures in `pending` instead of fabricating candidates.
- [Risk] Species-level Pokédex entries do not directly enumerate every form exposed by `/pokemon/`. -> Mitigation: compare against `species.name` on fetched Pokemon summaries and keep form handling explicit in tests.
- [Risk] Filtering can reduce available candidates below six for narrow type filters or unavailable data. -> Mitigation: return partial validated results with `pending` issues, as the team builder already does.
- [Risk] Additional Pokédex requests add latency. -> Mitigation: fetch the small membership set once per candidate query and intersect before detail requests.
