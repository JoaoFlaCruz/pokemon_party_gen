"""Fetch moves learned by one Pokemon from a PokeAPI-compatible REST API."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

from mcp_server.src.config.env import POKEAPI_BASE_URL, POKEAPI_MAX_WORKERS, POKEAPI_TIMEOUT


@dataclass(frozen=True)
class PokemonMoveSummary:
    """Pokemon move response enriched with move details."""

    pokemon_id: int
    pokemon_name: str
    stats: dict[str, int | None]
    moves: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "pokemon": {
                "id": self.pokemon_id,
                "name": self.pokemon_name,
                "stats": self.stats,
            },
            "moves": self.moves,
        }


class PokemonMovesFetcher:
    """Client for fetching every move learned by a Pokemon and move details."""

    DETAIL_FIELDS = (
        "id",
        "name",
        "accuracy",
        "effect_chance",
        "pp",
        "priority",
        "power",
        "damage_class",
        "generation",
        "meta",
        "stat_changes",
        "target",
        "type",
    )

    def __init__(
        self,
        base_url: str = POKEAPI_BASE_URL,
        timeout: float = POKEAPI_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

    def fetch_pokemon_moves(
        self,
        pokemon: str | int,
        max_workers: int = POKEAPI_MAX_WORKERS,
    ) -> dict[str, Any]:
        """Return all moves learned by one Pokemon, enriched with move detail data.

        Args:
            pokemon: Pokemon name or numeric id accepted by the PokeAPI
                ``pokemon/{id or name}/`` endpoint.
            max_workers: Number of parallel requests used for move detail calls.
        """
        payload = self._get_json(f"pokemon/{quote(str(pokemon).strip().lower())}/")
        moves = payload.get("moves", [])

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            detail_by_name = dict(executor.map(self._fetch_move_detail_pair, moves))

        enriched_moves = [
            {
                "move": move["move"],
                "version_group_details": move.get("version_group_details", []),
                "details": detail_by_name[move["move"]["name"]],
            }
            for move in moves
        ]

        stats = {
            item["stat"]["name"]: item.get("base_stat")
            for item in payload.get("stats", [])
        }

        return PokemonMoveSummary(
            pokemon_id=payload["id"],
            pokemon_name=payload["name"],
            stats=stats,
            moves=enriched_moves,
        ).to_dict()

    def _fetch_move_detail_pair(
        self,
        pokemon_move: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        move_name = pokemon_move["move"]["name"]
        return move_name, self._fetch_move_detail(move_name)

    def _fetch_move_detail(self, move: str) -> dict[str, Any]:
        payload = self._get_json(f"move/{quote(move)}/")
        return {
            field: payload.get(field)
            for field in self.DETAIL_FIELDS
        }

    def _get_json(self, path: str) -> dict[str, Any]:
        url = urljoin(self.base_url, path)
        request = Request(url, headers={"Accept": "application/json"})

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"API request failed with HTTP {exc.code}: {url}") from exc
        except URLError as exc:
            raise RuntimeError(f"API request failed: {url}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch all moves learned by a Pokemon with move details."
    )
    parser.add_argument("pokemon", help="Pokemon name or id, such as pikachu or 25.")
    parser.add_argument("--base-url", default=POKEAPI_BASE_URL)
    parser.add_argument("--timeout", type=float, default=POKEAPI_TIMEOUT)
    parser.add_argument("--max-workers", type=int, default=POKEAPI_MAX_WORKERS)
    args = parser.parse_args()

    fetcher = PokemonMovesFetcher(base_url=args.base_url, timeout=args.timeout)
    result = fetcher.fetch_pokemon_moves(
        pokemon=args.pokemon,
        max_workers=args.max_workers,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
