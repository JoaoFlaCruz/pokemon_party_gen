"""Tests for fetcher data shaping."""

from __future__ import annotations

import unittest
from typing import Any

from mcp_server.src.infrastructure.pokeapi.pokemon_fetcher import PokemonFetcher
from mcp_server.src.infrastructure.pokeapi.item_fetcher import ItemFetcher
from mcp_server.src.infrastructure.pokeapi.type_relations_fetcher import TypeRelationsFetcher


class FakePokemonFetcher(PokemonFetcher):
    def __init__(self, payloads: dict[str, dict[str, Any]]) -> None:
        super().__init__()
        self.payloads = payloads
        self.calls: list[str] = []

    def _get_json(self, path: str) -> dict[str, Any]:
        self.calls.append(path)
        return self.payloads[path]


class PokemonFetcherTests(unittest.TestCase):
    def test_fetch_pokemon_summary_excludes_legendary_species(self) -> None:
        fetcher = FakePokemonFetcher(
            {
                "pokemon/rayquaza/": {
                    "id": 384,
                    "name": "rayquaza",
                    "species": {"name": "rayquaza"},
                    "forms": [{"name": "rayquaza"}],
                    "stats": [],
                },
                "pokemon-species/rayquaza/": {
                    "is_legendary": True,
                    "is_mythical": False,
                },
            }
        )

        result = fetcher._fetch_pokemon_summary("rayquaza")

        self.assertIsNone(result)
        self.assertEqual(fetcher.calls, ["pokemon/rayquaza/", "pokemon-species/rayquaza/"])

    def test_fetch_pokemon_summary_enriches_mega_metadata_and_item(self) -> None:
        fetcher = FakePokemonFetcher(
            {
                "pokemon/venusaur-mega/": {
                    "id": 10033,
                    "name": "venusaur-mega",
                    "species": {"name": "venusaur"},
                    "forms": [{"name": "venusaur-mega"}],
                    "stats": [
                        {"stat": {"name": "hp"}, "base_stat": 80},
                        {"stat": {"name": "attack"}, "base_stat": 100},
                    ],
                },
                "pokemon-species/venusaur/": {
                    "is_legendary": False,
                    "is_mythical": False,
                },
                "pokemon-form/venusaur-mega/": {
                    "is_mega": True,
                    "is_battle_only": False,
                },
                "item/venusaurite/": {
                    "id": 659,
                    "name": "venusaurite",
                    "category": {"name": "mega-stones"},
                },
            }
        )

        result = fetcher._fetch_pokemon_summary("venusaur-mega")

        self.assertIsNotNone(result)
        data = result.to_dict()
        self.assertEqual(data["name"], "venusaur-mega")
        self.assertFalse(data["is_legendary"])
        self.assertTrue(data["is_mega"])
        self.assertFalse(data["is_battle_only"])
        self.assertEqual(data["base_pokemon"], "venusaur")
        self.assertEqual(data["required_item"]["name"], "venusaurite")
        self.assertEqual(data["required_item"]["category"]["name"], "mega-stones")

    def test_fetch_pokemon_summary_excludes_battle_only_forms(self) -> None:
        fetcher = FakePokemonFetcher(
            {
                "pokemon/aegislash-blade/": {
                    "id": 10026,
                    "name": "aegislash-blade",
                    "species": {"name": "aegislash"},
                    "forms": [{"name": "aegislash-blade"}],
                    "stats": [],
                },
                "pokemon-species/aegislash/": {
                    "is_legendary": False,
                    "is_mythical": False,
                },
                "pokemon-form/aegislash-blade/": {
                    "is_mega": False,
                    "is_battle_only": True,
                },
            }
        )

        result = fetcher._fetch_pokemon_summary("aegislash-blade")

        self.assertIsNone(result)
        self.assertEqual(
            fetcher.calls,
            [
                "pokemon/aegislash-blade/",
                "pokemon-species/aegislash/",
                "pokemon-form/aegislash-blade/",
            ],
        )

    def test_mega_item_name_handles_x_and_y_suffixes(self) -> None:
        self.assertEqual(PokemonFetcher._mega_item_name("charizard-mega-x"), "charizardite-x")
        self.assertEqual(PokemonFetcher._mega_item_name("mewtwo-mega-y"), "mewtwoite-y")


class FakeItemFetcher(ItemFetcher):
    def __init__(self, payloads: dict[str, dict[str, Any]]) -> None:
        super().__init__()
        self.payloads = payloads
        self.calls: list[str] = []

    def _get_json(self, path: str) -> dict[str, Any]:
        self.calls.append(path)
        return self.payloads[path]


class ItemFetcherTests(unittest.TestCase):
    def test_fetch_items_enriches_item_details(self) -> None:
        fetcher = FakeItemFetcher(
            {
                "item/?limit=1&offset=0": {
                    "count": 2,
                    "next": "http://localhost/api/v2/item/?offset=1&limit=1",
                    "previous": None,
                    "results": [
                        {
                            "name": "oran-berry",
                            "url": "http://localhost/api/v2/item/oran-berry/",
                        }
                    ],
                },
                "item/oran-berry/": {
                    "id": 132,
                    "name": "oran-berry",
                    "cost": 80,
                    "fling_power": 10,
                    "fling_effect": {
                        "name": "berry-effect",
                        "url": "http://localhost/api/v2/item-fling-effect/3/",
                    },
                    "attributes": [
                        {
                            "name": "holdable",
                            "url": "http://localhost/api/v2/item-attribute/5/",
                        }
                    ],
                    "category": {
                        "name": "medicine",
                        "url": "http://localhost/api/v2/item-category/27/",
                    },
                    "effect_entries": [
                        {
                            "effect": "Restores 10 HP.",
                            "short_effect": "Restores 10 HP.",
                            "language": {
                                "name": "en",
                                "url": "http://localhost/api/v2/language/9/",
                            },
                        }
                    ],
                    "flavor_text_entries": [],
                    "sprites": {"default": "http://localhost/media/item.png"},
                },
            }
        )

        result = fetcher.fetch_items(limit=1, offset=0, max_workers=1)

        self.assertEqual(fetcher.calls, ["item/?limit=1&offset=0", "item/oran-berry/"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["limit"], 1)
        self.assertEqual(result["offset"], 0)
        self.assertEqual(result["items"][0]["name"], "oran-berry")
        self.assertEqual(result["items"][0]["cost"], 80)
        self.assertEqual(result["items"][0]["category"]["name"], "medicine")
        self.assertEqual(result["items"][0]["attributes"][0]["name"], "holdable")

    def test_fetch_items_returns_empty_list_without_results(self) -> None:
        fetcher = FakeItemFetcher(
            {
                "item/?limit=5&offset=10": {
                    "count": 0,
                    "next": None,
                    "previous": None,
                    "results": [],
                }
            }
        )

        result = fetcher.fetch_items(limit=5, offset=10, max_workers=1)

        self.assertEqual(result["items"], [])
        self.assertEqual(fetcher.calls, ["item/?limit=5&offset=10"])


class FakeTypeRelationsFetcher(TypeRelationsFetcher):
    def __init__(self, payloads: dict[str, dict[str, Any]]) -> None:
        super().__init__()
        self.payloads = payloads
        self.calls: list[str] = []

    def _get_json(self, path: str) -> dict[str, Any]:
        self.calls.append(path)
        return self.payloads[path]


class TypeRelationsFetcherTests(unittest.TestCase):
    def test_fetch_type_relations_normalizes_damage_relations(self) -> None:
        fetcher = FakeTypeRelationsFetcher(
            {
                "type/fire/": {
                    "id": 10,
                    "name": "fire",
                    "damage_relations": {
                        "double_damage_to": [
                            {"name": "grass"},
                            {"name": "ice"},
                        ],
                        "half_damage_to": [
                            {"name": "water"},
                        ],
                        "no_damage_to": [],
                        "double_damage_from": [
                            {"name": "water"},
                            {"name": "rock"},
                        ],
                        "half_damage_from": [
                            {"name": "fire"},
                            {"name": "grass"},
                        ],
                        "no_damage_from": [],
                    },
                }
            }
        )

        result = fetcher.fetch_type_relations("Fire")

        self.assertEqual(fetcher.calls, ["type/fire/"])
        self.assertEqual(result["type"], {"id": 10, "name": "fire"})
        self.assertEqual(result["offensive"]["super_effective_against"], ["grass", "ice"])
        self.assertEqual(result["offensive"]["weak_against"], ["water"])
        self.assertEqual(result["offensive"]["no_effect_against"], [])
        self.assertEqual(result["defensive"]["weak_to"], ["water", "rock"])
        self.assertEqual(result["defensive"]["resists"], ["fire", "grass"])
        self.assertEqual(result["defensive"]["immune_to"], [])


if __name__ == "__main__":
    unittest.main()
