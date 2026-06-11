"""Rank Pokemon by defensive stats plus one selected offensive stat."""

from __future__ import annotations

import argparse
import json
from typing import Any, Protocol

from mcp_server.src.config.env import POKEAPI_BASE_URL, POKEAPI_MAX_WORKERS, POKEAPI_TIMEOUT
from mcp_server.src.infrastructure.pokeapi import PokemonFetcher

OFFENSE_AUTO = "auto"
OFFENSE_ATTACK = "attack"
OFFENSE_SPECIAL_ATTACK = "special-attack"
OFFENSE_CHOICES = (OFFENSE_AUTO, OFFENSE_ATTACK, OFFENSE_SPECIAL_ATTACK)
STAT_HP = "hp"
STAT_DEFENSE = "defense"
STAT_SPECIAL_DEFENSE = "special-defense"
STAT_SPEED = "speed"
PRIORITY_STAT_CHOICES = (
    STAT_HP,
    OFFENSE_ATTACK,
    STAT_DEFENSE,
    OFFENSE_SPECIAL_ATTACK,
    STAT_SPECIAL_DEFENSE,
    STAT_SPEED,
)
SPEED_IGNORE = "ignore"
SPEED_HIGH = "high"
SPEED_LOW = "low"
SPEED_MODE_CHOICES = (SPEED_IGNORE, SPEED_HIGH, SPEED_LOW)
PRIORITY_MULTIPLIER = 1.4
MAX_BASE_SPEED = 255


class FetchesPokemon(Protocol):
    def fetch_pokemon(
        self,
        types: list[str] | tuple[str, ...] | None = None,
        ability: str | None = None,
        move: str | None = None,
        champions_only: bool = False,
        allowed_species: set[str] | None = None,
        max_workers: int = POKEAPI_MAX_WORKERS,
    ) -> list[dict[str, Any]]:
        ...


def normalize_types(types: list[str] | tuple[str, ...] | None) -> list[str] | None:
    """Normalize up to two type filters, accepting empty/null-like values."""
    if not types:
        return None

    normalized = [
        value.strip().lower()
        for value in types
        if value and value.strip() and value.strip().lower() not in {"null", "none"}
    ]
    if len(normalized) > 2:
        raise ValueError("Use no máximo dois tipos por consulta.")

    return normalized or None


def stat_value(stats: dict[str, int | None], stat_name: str) -> int:
    return stats.get(stat_name) or 0


def validate_priority_stat(priority_stat: str | None) -> str | None:
    if priority_stat is None:
        return None
    if priority_stat not in PRIORITY_STAT_CHOICES:
        raise ValueError(
            "priority_stat deve ser hp, attack, defense, special-attack, "
            "special-defense ou speed."
        )
    return priority_stat


def validate_speed_mode(speed_mode: str = SPEED_IGNORE) -> str:
    if speed_mode not in SPEED_MODE_CHOICES:
        raise ValueError("speed_mode deve ser ignore, high ou low.")
    return speed_mode


def select_offense_stat(
    stats: dict[str, int | None],
    offense_stat: str = OFFENSE_AUTO,
) -> tuple[str, str]:
    """Return selected and ignored offensive stat names."""
    if offense_stat == OFFENSE_ATTACK:
        return OFFENSE_ATTACK, OFFENSE_SPECIAL_ATTACK
    if offense_stat == OFFENSE_SPECIAL_ATTACK:
        return OFFENSE_SPECIAL_ATTACK, OFFENSE_ATTACK
    if offense_stat != OFFENSE_AUTO:
        raise ValueError("offense_stat deve ser auto, attack ou special-attack.")

    attack = stat_value(stats, OFFENSE_ATTACK)
    special_attack = stat_value(stats, OFFENSE_SPECIAL_ATTACK)
    if attack >= special_attack:
        return OFFENSE_ATTACK, OFFENSE_SPECIAL_ATTACK
    return OFFENSE_SPECIAL_ATTACK, OFFENSE_ATTACK


def score_pokemon(
    pokemon: dict[str, Any],
    offense_stat: str = OFFENSE_AUTO,
    priority_stat: str | None = None,
    speed_mode: str = SPEED_IGNORE,
) -> dict[str, Any]:
    """Score one Pokemon, optionally prioritizing one stat with a multiplier."""
    priority_stat = validate_priority_stat(priority_stat)
    speed_mode = validate_speed_mode(speed_mode)
    stats = pokemon.get("stats", {})
    selected_offense, ignored_offense = select_offense_stat(stats, offense_stat)
    score_parts = {
        STAT_HP: stat_value(stats, STAT_HP),
        STAT_DEFENSE: stat_value(stats, STAT_DEFENSE),
        STAT_SPECIAL_DEFENSE: stat_value(stats, STAT_SPECIAL_DEFENSE),
        selected_offense: stat_value(stats, selected_offense),
    }

    if priority_stat and priority_stat != STAT_SPEED:
        score_parts[priority_stat] = stat_value(stats, priority_stat)

    if speed_mode == SPEED_HIGH:
        score_parts[STAT_SPEED] = stat_value(stats, STAT_SPEED)
    elif speed_mode == SPEED_LOW:
        score_parts[STAT_SPEED] = max(0, MAX_BASE_SPEED - stat_value(stats, STAT_SPEED))

    weighted_score_parts: dict[str, float] = {}
    for stat_name, value in score_parts.items():
        multiplier = PRIORITY_MULTIPLIER if stat_name == priority_stat else 1.0
        weighted_score_parts[stat_name] = value * multiplier

    ignored_stats = [
        stat_name
        for stat_name in PRIORITY_STAT_CHOICES
        if stat_name not in score_parts
    ]

    result = {
        "name": pokemon["name"],
        "score": sum(weighted_score_parts.values()),
        "selected_offense_stat": selected_offense,
        "priority_stat": priority_stat,
        "priority_multiplier": PRIORITY_MULTIPLIER if priority_stat else None,
        "speed_mode": speed_mode,
        "ignored_stats": ignored_stats,
        "score_parts": score_parts,
        "weighted_score_parts": weighted_score_parts,
        "stats": stats,
    }
    for field in (
        "species",
        "is_legendary",
        "is_mythical",
        "is_mega",
        "is_battle_only",
        "base_pokemon",
        "required_item",
        "champions_dex",
        "id",
    ):
        if field in pokemon:
            result[field] = pokemon[field]

    return result


def rank_pokemon(
    fetcher: FetchesPokemon,
    types: list[str] | tuple[str, ...] | None = None,
    offense_stat: str = OFFENSE_AUTO,
    priority_stat: str | None = None,
    speed_mode: str = SPEED_IGNORE,
    head_size: int = 10,
    champions_only: bool = False,
    allowed_species: set[str] | None = None,
    max_workers: int = POKEAPI_MAX_WORKERS,
) -> list[dict[str, Any]]:
    """Fetch Pokemon, score them, and return the best entries first."""
    if head_size < 1:
        raise ValueError("head_size deve ser maior que zero.")

    normalized_types = normalize_types(types)
    pokemon_list = fetcher.fetch_pokemon(
        types=normalized_types,
        champions_only=champions_only,
        allowed_species=allowed_species,
        max_workers=max_workers,
    )
    ranked = [
        score_pokemon(
            pokemon,
            offense_stat=offense_stat,
            priority_stat=priority_stat,
            speed_mode=speed_mode,
        )
        for pokemon in pokemon_list
    ]
    ranked.sort(key=lambda item: (-item["score"], item["name"]))
    return ranked[:head_size]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Rank Pokemon by hp + defense + special-defense + one offensive stat, "
            "always ignoring speed."
        )
    )
    parser.add_argument(
        "--type",
        dest="types",
        action="append",
        default=None,
        help="Optional Pokemon type filter. Repeat up to two times; null/none is ignored.",
    )
    parser.add_argument(
        "--offense-stat",
        choices=OFFENSE_CHOICES,
        default=OFFENSE_AUTO,
        help="Use auto to choose the greater stat per Pokemon, or force one stat manually.",
    )
    parser.add_argument(
        "--priority-stat",
        choices=PRIORITY_STAT_CHOICES,
        default=None,
        help="Optional stat that receives a 1.4 multiplier in the score.",
    )
    parser.add_argument(
        "--speed-mode",
        choices=SPEED_MODE_CHOICES,
        default=SPEED_IGNORE,
        help="Use high to favor fast Pokemon, low to favor slow Pokemon, or ignore.",
    )
    parser.add_argument(
        "--head-size",
        type=int,
        default=10,
        help="Maximum number of best Pokemon returned.",
    )
    parser.add_argument("--base-url", default=POKEAPI_BASE_URL)
    parser.add_argument("--timeout", type=float, default=POKEAPI_TIMEOUT)
    parser.add_argument("--champions-only", action="store_true")
    parser.add_argument("--max-workers", type=int, default=POKEAPI_MAX_WORKERS)
    args = parser.parse_args()

    fetcher = PokemonFetcher(base_url=args.base_url, timeout=args.timeout)
    result = rank_pokemon(
        fetcher=fetcher,
        types=args.types,
        offense_stat=args.offense_stat,
        priority_stat=args.priority_stat,
        speed_mode=args.speed_mode,
        head_size=args.head_size,
        champions_only=args.champions_only,
        max_workers=args.max_workers,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
