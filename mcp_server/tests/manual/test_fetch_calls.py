"""Manual API call checks for the Pokemon fetcher.

Run after the PokeAPI Docker stack is up and the database is populated:
python3 -m mcp_server.tests.manual.test_fetch_calls
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from mcp_server.src.infrastructure.pokeapi import ItemFetcher, PokemonFetcher, PokemonMovesFetcher

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def print_sample(label: str, data: list[dict], limit: int = 5) -> None:
    print(f"\n{label}: {len(data)} resultado(s)")
    print(json.dumps(data[:limit], indent=2, ensure_ascii=False))


def print_pokemon_moves_sample(label: str, data: dict, limit: int = 5) -> None:
    pokemon = data["pokemon"]
    moves = data["moves"]
    print(f"\n{label}: {pokemon['name']} ({len(moves)} golpe(s))")
    print(json.dumps(moves[:limit], indent=2, ensure_ascii=False))


def print_items_sample(label: str, data: dict, limit: int = 5) -> None:
    items = data["items"]
    print(f"\n{label}: {len(items)} item(ns)")
    print(json.dumps(items[:limit], indent=2, ensure_ascii=False))


def main() -> None:
    moves_fetcher = PokemonMovesFetcher()

    #print_sample("Todos os Pokemon", fetcher.fetch_pokemon())
    #print_sample("Tipo fire", fetcher.fetch_pokemon(types=["fire"]))
    #print_sample("Tipos water + flying", fetcher.fetch_pokemon(types=["water", "flying"]))
    #print_sample("Habilidade overgrow", fetcher.fetch_pokemon(ability="overgrow"))
    #print_sample("Ataque thunder-punch", fetcher.fetch_pokemon(move="thunder-punch"))
    #print_sample(
    #    "Filtro combinado",
    #    fetcher.fetch_pokemon(types=["grass"], ability="overgrow"),
    #)
    print_pokemon_moves_sample(
        "Golpes do Bulbasaur",
        moves_fetcher.fetch_pokemon_moves("bulbasaur"),
    )
    #print_items_sample(
    #    "Itens gerais",
    #    item_fetcher.fetch_items(limit=5),
    #)


if __name__ == "__main__":
    main()
