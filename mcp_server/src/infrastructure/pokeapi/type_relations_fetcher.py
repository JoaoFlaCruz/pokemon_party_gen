"""Fetch Pokemon type damage relations from a PokeAPI-compatible REST API."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

from mcp_server.src.config.env import POKEAPI_BASE_URL, POKEAPI_TIMEOUT


@dataclass(frozen=True)
class TypeRelationsSummary:
    """Type damage relations normalized for callers."""

    type_id: int
    type_name: str
    offensive: dict[str, list[str]]
    defensive: dict[str, list[str]]
    raw_damage_relations: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": {
                "id": self.type_id,
                "name": self.type_name,
            },
            "offensive": self.offensive,
            "defensive": self.defensive,
            "raw_damage_relations": self.raw_damage_relations,
        }


class TypeRelationsFetcher:
    """Client for fetching type effectiveness relationships."""

    def __init__(
        self,
        base_url: str = POKEAPI_BASE_URL,
        timeout: float = POKEAPI_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

    def fetch_type_relations(self, pokemon_type: str | int) -> dict[str, Any]:
        """Return offensive and defensive relationships for one Pokemon type.

        Args:
            pokemon_type: Type name or numeric id accepted by the PokeAPI
                ``type/{id or name}/`` endpoint.
        """
        payload = self._get_json(f"type/{quote(str(pokemon_type).strip().lower())}/")
        damage_relations = payload.get("damage_relations", {})

        return TypeRelationsSummary(
            type_id=payload["id"],
            type_name=payload["name"],
            offensive={
                "super_effective_against": self._relation_names(
                    damage_relations,
                    "double_damage_to",
                ),
                "weak_against": self._relation_names(
                    damage_relations,
                    "half_damage_to",
                ),
                "no_effect_against": self._relation_names(
                    damage_relations,
                    "no_damage_to",
                ),
            },
            defensive={
                "weak_to": self._relation_names(
                    damage_relations,
                    "double_damage_from",
                ),
                "resists": self._relation_names(
                    damage_relations,
                    "half_damage_from",
                ),
                "immune_to": self._relation_names(
                    damage_relations,
                    "no_damage_from",
                ),
            },
            raw_damage_relations=damage_relations,
        ).to_dict()

    @staticmethod
    def _relation_names(damage_relations: dict[str, Any], field: str) -> list[str]:
        return [item["name"] for item in damage_relations.get(field, [])]

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
        description="Fetch offensive and defensive damage relations for one Pokemon type."
    )
    parser.add_argument("type", help="Type name or id, such as fire or 10.")
    parser.add_argument("--base-url", default=POKEAPI_BASE_URL)
    parser.add_argument("--timeout", type=float, default=POKEAPI_TIMEOUT)
    args = parser.parse_args()

    fetcher = TypeRelationsFetcher(base_url=args.base_url, timeout=args.timeout)
    result = fetcher.fetch_type_relations(args.type)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
