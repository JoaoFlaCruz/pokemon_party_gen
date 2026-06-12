"""Fetch Pokemon data from a PokeAPI-compatible REST API."""

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
class PokemonSummary:
    """Pokemon response used by ranking callers."""

    name: str
    stats: dict[str, int | None]
    species: dict[str, Any]
    is_legendary: bool
    is_mythical: bool
    is_mega: bool
    is_battle_only: bool
    base_pokemon: str | None = None
    required_item: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "stats": self.stats,
            "species": self.species,
            "is_legendary": self.is_legendary,
            "is_mythical": self.is_mythical,
            "is_mega": self.is_mega,
            "is_battle_only": self.is_battle_only,
            "base_pokemon": self.base_pokemon,
            "required_item": self.required_item,
        }


class PokemonFetcher:
    """Client for fetching Pokemon names and stats with optional filters."""

    def __init__(
        self,
        base_url: str = POKEAPI_BASE_URL,
        timeout: float = POKEAPI_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

    def fetch_pokemon(
        self,
        types: list[str] | tuple[str, ...] | None = None,
        ability: str | None = None,
        move: str | None = None,
        max_workers: int = POKEAPI_MAX_WORKERS,
    ) -> list[dict[str, Any]]:
        """Return Pokemon with name and stats, filtered by type, ability, and move.

        Args:
            types: Optional list with one or two type names, such as ["fire"] or
                ["water", "flying"]. When omitted or None, all types are accepted.
            ability: Optional ability identifier, such as "overgrow".
            move: Optional move/attack identifier, such as "thunder-punch".
            max_workers: Number of parallel requests used for Pokemon detail calls.
        """
        normalized_types = self._normalize_types(types)
        candidate_names = self._candidate_names(normalized_types, ability, move)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            summaries = executor.map(self._fetch_pokemon_summary, sorted(candidate_names))

        return [summary.to_dict() for summary in summaries if summary is not None]

    def _candidate_names(
        self,
        types: tuple[str, ...],
        ability: str | None,
        move: str | None,
    ) -> set[str]:
        filter_sets: list[set[str]] = []

        for pokemon_type in types:
            filter_sets.append(self._pokemon_names_by_type(pokemon_type))

        if ability:
            filter_sets.append(self._pokemon_names_by_ability(ability))

        if move:
            filter_sets.append(self._pokemon_names_by_move(move))

        if not filter_sets:
            return self._all_pokemon_names()

        return set.intersection(*filter_sets)

    def _all_pokemon_names(self) -> set[str]:
        payload = self._get_json("pokemon/?limit=100000&offset=0")
        return {item["name"] for item in payload["results"]}

    def _pokemon_names_by_type(self, pokemon_type: str) -> set[str]:
        payload = self._get_json(f"type/{quote(pokemon_type)}/")
        return {item["pokemon"]["name"] for item in payload["pokemon"]}

    def _pokemon_names_by_ability(self, ability: str) -> set[str]:
        payload = self._get_json(f"ability/{quote(ability)}/")
        return {item["pokemon"]["name"] for item in payload["pokemon"]}

    def _pokemon_names_by_move(self, move: str) -> set[str]:
        payload = self._get_json(f"move/{quote(move)}/")
        return {item["name"] for item in payload["learned_by_pokemon"]}

    def _fetch_pokemon_summary(self, name: str) -> PokemonSummary | None:
        payload = self._get_json(f"pokemon/{quote(name)}/")
        species_ref = payload.get("species") or {}
        species_name = species_ref.get("name")
        species_payload = self._fetch_species(species_name) if species_name else {}
        if species_payload.get("is_legendary") is True:
            return None

        form_payload = self._fetch_default_form(payload)
        if form_payload.get("is_battle_only") is True:
            return None

        is_mega = bool(form_payload.get("is_mega"))
        stats = {
            item["stat"]["name"]: item.get("base_stat")
            for item in payload.get("stats", [])
        }
        return PokemonSummary(
            name=payload["name"],
            stats=stats,
            species=species_ref,
            is_legendary=bool(species_payload.get("is_legendary")),
            is_mythical=bool(species_payload.get("is_mythical")),
            is_mega=is_mega,
            is_battle_only=bool(form_payload.get("is_battle_only")),
            base_pokemon=species_name if is_mega else None,
            required_item=self._mega_required_item(payload["name"]) if is_mega else None,
        )

    def _fetch_species(self, species_name: str) -> dict[str, Any]:
        return self._get_json(f"pokemon-species/{quote(species_name)}/")

    def _fetch_default_form(self, pokemon_payload: dict[str, Any]) -> dict[str, Any]:
        forms = pokemon_payload.get("forms", [])
        for form in forms:
            form_name = form.get("name")
            if form_name == pokemon_payload.get("name"):
                return self._get_json(f"pokemon-form/{quote(form_name)}/")

        if forms:
            form_name = forms[0].get("name")
            if form_name:
                return self._get_json(f"pokemon-form/{quote(form_name)}/")

        return {}

    def _mega_required_item(self, pokemon_name: str) -> dict[str, Any] | None:
        item_name = self._mega_item_name(pokemon_name)
        if not item_name:
            return None

        try:
            item_payload = self._get_json(f"item/{quote(item_name)}/")
        except RuntimeError:
            return None

        return {
            "id": item_payload.get("id"),
            "name": item_payload.get("name"),
            "category": item_payload.get("category"),
        }

    @staticmethod
    def _mega_item_name(pokemon_name: str) -> str | None:
        marker = "-mega"
        if marker not in pokemon_name:
            return None

        base, suffix = pokemon_name.split(marker, 1)
        return f"{base}ite{suffix}"

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

    @staticmethod
    def _normalize_types(types: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
        if not types:
            return ()

        normalized = tuple(item.strip().lower() for item in types if item and item.strip())
        if len(normalized) > 2:
            raise ValueError("Use no máximo dois tipos por consulta.")

        return normalized


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Pokemon names and stats.")
    parser.add_argument("--base-url", default=POKEAPI_BASE_URL)
    parser.add_argument("--timeout", type=float, default=POKEAPI_TIMEOUT)
    parser.add_argument("--max-workers", type=int, default=POKEAPI_MAX_WORKERS)
    parser.add_argument("--type", dest="types", action="append", default=None)
    parser.add_argument("--ability", default=None)
    parser.add_argument("--move", default=None)
    args = parser.parse_args()

    fetcher = PokemonFetcher(base_url=args.base_url, timeout=args.timeout)
    result = fetcher.fetch_pokemon(
        types=args.types,
        ability=args.ability,
        move=args.move,
        max_workers=args.max_workers,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
