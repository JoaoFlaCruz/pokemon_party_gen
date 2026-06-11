"""Rank a Pokemon moveset using move power and accuracy."""

from __future__ import annotations

import argparse
import json
from typing import Any, Protocol

from mcp_server.src.config.env import (
    POKEAPI_BASE_URL,
    POKEAPI_MAX_WORKERS,
    POKEAPI_TIMEOUT,
)
from mcp_server.src.infrastructure.pokeapi import PokemonMovesFetcher

ATTACK = "attack"
SPECIAL_ATTACK = "special-attack"
PHYSICAL = "physical"
SPECIAL = "special"
STATUS = "status"
ACCURACY_WEIGHT = 1.4


class FetchesPokemonMoves(Protocol):
    def fetch_pokemon_moves(
        self,
        pokemon: str | int,
        max_workers: int = POKEAPI_MAX_WORKERS,
    ) -> dict[str, Any]: ...


def stat_value(stats: dict[str, int | None], stat_name: str) -> int:
    return stats.get(stat_name) or 0


def best_offense(stats: dict[str, int | None]) -> tuple[str, str]:
    """Return the Pokemon best offensive stat and matching move damage class."""
    if stat_value(stats, ATTACK) >= stat_value(stats, SPECIAL_ATTACK):
        return ATTACK, PHYSICAL
    return SPECIAL_ATTACK, SPECIAL


def move_detail(move: dict[str, Any], field: str) -> Any:
    return move.get("details", {}).get(field)


def move_damage_class(move: dict[str, Any]) -> str | None:
    damage_class = move_detail(move, "damage_class") or {}
    return damage_class.get("name")


def numeric_move_detail(move: dict[str, Any], field: str) -> int:
    return move_detail(move, field) or 0


def move_name(move: dict[str, Any]) -> str:
    details_name = move.get("details", {}).get("name")
    if details_name:
        return details_name
    return move.get("move", {}).get("name", "")


def is_status_move(move: dict[str, Any]) -> bool:
    return move_damage_class(move) == STATUS


def move_score(move: dict[str, Any]) -> float:
    accuracy = numeric_move_detail(move, "accuracy")
    power = numeric_move_detail(move, "power")
    return accuracy * ACCURACY_WEIGHT + power


def summarize_move(
    move: dict[str, Any],
    rank: int | None,
    score: float | None,
    category: str,
) -> dict[str, Any]:
    details = move.get("details", {})
    return {
        "rank": rank,
        "name": move_name(move),
        "category": category,
        "score": score,
        "accuracy": details.get("accuracy"),
        "power": details.get("power"),
        "damage_class": move_damage_class(move),
        "type": (details.get("type") or {}).get("name"),
        "pp": details.get("pp"),
        "priority": details.get("priority"),
        "version_group_details": move.get("version_group_details", []),
    }


def rank_moveset_data(data: dict[str, Any]) -> dict[str, Any]:
    """Rank fetched moves for one Pokemon using the requested moveset rule."""
    pokemon = data["pokemon"]
    stats = pokemon.get("stats", {})
    selected_stat, selected_damage_class = best_offense(stats)
    ranked_moves = []
    status_moves = []

    for move in data.get("moves", []):
        damage_class = move_damage_class(move)
        if is_status_move(move):
            status_moves.append(move)
        elif damage_class == selected_damage_class:
            ranked_moves.append(move)

    ranked_moves.sort(
        key=lambda move: (
            -move_score(move),
            -numeric_move_detail(move, "accuracy"),
            -numeric_move_detail(move, "power"),
            move_name(move),
        )
    )

    result_moves = [
        summarize_move(move, rank=index, score=move_score(move), category="ranked")
        for index, move in enumerate(ranked_moves, start=1)
    ]
    result_moves.extend(
        summarize_move(move, rank=None, score=None, category="status")
        for move in status_moves
    )

    return {
        "pokemon": pokemon,
        "selected_offense_stat": selected_stat,
        "selected_damage_class": selected_damage_class,
        "ranking_rule": "accuracy * 1.4 + power",
        "moves": result_moves,
    }


def rank_pokemon_moveset(
    pokemon: str | int,
    fetcher: FetchesPokemonMoves | None = None,
    max_workers: int = POKEAPI_MAX_WORKERS,
) -> dict[str, Any]:
    """Fetch one Pokemon moveset and rank it."""
    moves_fetcher = fetcher or PokemonMovesFetcher()
    data = moves_fetcher.fetch_pokemon_moves(pokemon, max_workers=max_workers)
    return rank_moveset_data(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank one Pokemon moveset.")
    parser.add_argument("pokemon", help="Pokemon name or id, such as bulbasaur or 1.")
    parser.add_argument("--base-url", default=POKEAPI_BASE_URL)
    parser.add_argument("--timeout", type=float, default=POKEAPI_TIMEOUT)
    parser.add_argument("--max-workers", type=int, default=POKEAPI_MAX_WORKERS)
    args = parser.parse_args()

    fetcher = PokemonMovesFetcher(base_url=args.base_url, timeout=args.timeout)
    result = rank_pokemon_moveset(
        pokemon=args.pokemon,
        fetcher=fetcher,
        max_workers=args.max_workers,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
