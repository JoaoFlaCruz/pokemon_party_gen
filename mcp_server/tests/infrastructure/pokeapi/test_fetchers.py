"""Tests for fetcher data shaping."""

from __future__ import annotations

import unittest
from typing import Any

from mcp_server.src.infrastructure.pokeapi.champions_dex_fetcher import (
    ChampionsDexFetcher,
    champions_species_from_payload,
)
from mcp_server.src.infrastructure.pokeapi.pokemon_fetcher import PokemonFetcher
from mcp_server.src.infrastructure.pokeapi.pokemon_moves_fetcher import PokemonMovesFetcher
from mcp_server.src.infrastructure.pokeapi.item_fetcher import ItemFetcher
from mcp_server.src.infrastructure.pokeapi.type_relations_fetcher import TypeRelationsFetcher


class FakeChampionsDexFetcher(ChampionsDexFetcher):
    def __init__(self, payloads: dict[str, dict[str, Any]]) -> None:
        super().__init__()
        self.payloads = payloads
        self.calls: list[str] = []

    def _get_json(self, path: str) -> dict[str, Any]:
        self.calls.append(path)
        payload = self.payloads[path]
        if "error" in payload:
            raise RuntimeError(payload["error"])
        return payload


class ChampionsDexFetcherTests(unittest.TestCase):
    def test_extracts_normalized_species_from_pokedex_payload(self) -> None:
        result = champions_species_from_payload(
            {
                "pokemon_entries": [
                    {"pokemon_species": {"name": " Venusaur "}},
                    {"pokemon_species": {"name": "charizard"}},
                    {"pokemon_species": {}},
                ]
            }
        )

        self.assertEqual(result, {"venusaur", "charizard"})

    def test_fetches_champions_by_identifier(self) -> None:
        fetcher = FakeChampionsDexFetcher(
            {
                "pokedex/champions/": {
                    "pokemon_entries": [{"pokemon_species": {"name": "venusaur"}}]
                }
            }
        )

        self.assertEqual(fetcher.fetch_champions_species(), {"venusaur"})
        self.assertEqual(fetcher.calls, ["pokedex/champions/"])

    def test_falls_back_to_numeric_champions_pokedex_id(self) -> None:
        fetcher = FakeChampionsDexFetcher(
            {
                "pokedex/champions/": {"error": "missing"},
                "pokedex/36/": {
                    "pokemon_entries": [{"pokemon_species": {"name": "pikachu"}}]
                },
            }
        )

        self.assertEqual(fetcher.fetch_champions_species(), {"pikachu"})
        self.assertEqual(fetcher.calls, ["pokedex/champions/", "pokedex/36/"])

    def test_reports_failure_when_champions_membership_is_unavailable(self) -> None:
        fetcher = FakeChampionsDexFetcher(
            {
                "pokedex/champions/": {"error": "missing"},
                "pokedex/36/": {"error": "offline"},
            }
        )

        with self.assertRaises(RuntimeError):
            fetcher.fetch_champions_species()


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
                        {"stat": {"name": "defense"}, "base_stat": 123},
                        {"stat": {"name": "special-attack"}, "base_stat": 122},
                        {"stat": {"name": "special-defense"}, "base_stat": 120},
                        {"stat": {"name": "speed"}, "base_stat": 80},
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


    def test_fetch_pokemon_filters_champions_candidates_by_allowed_species(self) -> None:
        fetcher = FakePokemonFetcher(
            {
                "pokemon/?limit=100000&offset=0": {
                    "results": [
                        {"name": "venusaur"},
                        {"name": "charizard"},
                    ]
                },
                "pokemon/venusaur/": {
                    "id": 3,
                    "name": "venusaur",
                    "species": {"name": "venusaur"},
                    "forms": [{"name": "venusaur"}],
                    "types": [
                        {"slot": 1, "type": {"name": "grass"}},
                        {"slot": 2, "type": {"name": "poison"}},
                    ],
                    "abilities": [
                        {"ability": {"name": "overgrow"}, "is_hidden": False, "slot": 1}
                    ],
                    "stats": [
                        {"stat": {"name": "hp"}, "base_stat": 80},
                        {"stat": {"name": "attack"}, "base_stat": 82},
                        {"stat": {"name": "defense"}, "base_stat": 83},
                        {"stat": {"name": "special-attack"}, "base_stat": 100},
                        {"stat": {"name": "special-defense"}, "base_stat": 100},
                        {"stat": {"name": "speed"}, "base_stat": 80},
                    ],
                },
                "pokemon-species/venusaur/": {
                    "is_legendary": False,
                    "is_mythical": False,
                },
                "pokemon-form/venusaur/": {
                    "is_mega": False,
                    "is_battle_only": False,
                },
            }
        )

        result = fetcher.fetch_pokemon(allowed_species={"venusaur"}, max_workers=1)

        self.assertEqual([pokemon["name"] for pokemon in result], ["venusaur"])
        self.assertTrue(result[0]["champions_dex"])
        self.assertNotIn("pokemon/charizard/", fetcher.calls)

    def test_fetch_pokemon_summary_excludes_incomplete_stats(self) -> None:
        fetcher = FakePokemonFetcher(
            {
                "pokemon/archaludon/": {
                    "id": 1018,
                    "name": "archaludon",
                    "species": {"name": "archaludon"},
                    "forms": [{"name": "archaludon"}],
                    "stats": [],
                },
                "pokemon-species/archaludon/": {
                    "is_legendary": False,
                    "is_mythical": False,
                },
                "pokemon-form/archaludon/": {
                    "is_mega": False,
                    "is_battle_only": False,
                },
            }
        )

        result = fetcher._fetch_pokemon_summary(
            "archaludon",
            champions_species={"archaludon"},
        )

        self.assertIsNone(result)

    def test_fetch_pokemon_detail_reports_complete_champions_data(self) -> None:
        fetcher = FakePokemonFetcher(
            {
                "pokemon/pelipper/": {
                    "id": 279,
                    "name": "pelipper",
                    "species": {"name": "pelipper"},
                    "forms": [{"name": "pelipper"}],
                    "types": [
                        {"slot": 1, "type": {"name": "water"}},
                        {"slot": 2, "type": {"name": "flying"}},
                    ],
                    "abilities": [
                        {"ability": {"name": "drizzle"}, "is_hidden": False, "slot": 1}
                    ],
                    "stats": [
                        {"stat": {"name": "hp"}, "base_stat": 60},
                        {"stat": {"name": "attack"}, "base_stat": 50},
                        {"stat": {"name": "defense"}, "base_stat": 100},
                        {"stat": {"name": "special-attack"}, "base_stat": 95},
                        {"stat": {"name": "special-defense"}, "base_stat": 70},
                        {"stat": {"name": "speed"}, "base_stat": 65},
                    ],
                },
                "pokemon-species/pelipper/": {
                    "is_legendary": False,
                    "is_mythical": False,
                },
                "pokemon-form/pelipper/": {
                    "is_mega": False,
                    "is_battle_only": False,
                },
            }
        )

        result = fetcher.fetch_pokemon_detail("pelipper", allowed_species={"pelipper"})

        self.assertTrue(result["complete"])
        self.assertTrue(result["eligible"])
        self.assertEqual(result["types"], ["water", "flying"])
        self.assertEqual(result["abilities"][0]["name"], "drizzle")
        self.assertTrue(result["champions_dex"])

    def test_fetch_pokemon_detail_reports_missing_fields_and_scope(self) -> None:
        fetcher = FakePokemonFetcher(
            {
                "pokemon/archaludon/": {
                    "id": 1018,
                    "name": "archaludon",
                    "species": {"name": "archaludon"},
                    "forms": [{"name": "archaludon"}],
                    "types": [],
                    "abilities": [],
                    "stats": [],
                },
                "pokemon-species/archaludon/": {
                    "is_legendary": False,
                    "is_mythical": False,
                },
                "pokemon-form/archaludon/": {
                    "is_mega": False,
                    "is_battle_only": False,
                },
            }
        )

        result = fetcher.fetch_pokemon_detail("archaludon", allowed_species={"pelipper"})

        self.assertFalse(result["complete"])
        self.assertFalse(result["eligible"])
        self.assertFalse(result["champions_dex"])
        self.assertIn("types", result["missing_fields"])
        self.assertIn("abilities", result["missing_fields"])

    def test_mega_item_name_handles_x_and_y_suffixes(self) -> None:
        self.assertEqual(PokemonFetcher._mega_item_name("charizard-mega-x"), "charizardite-x")
        self.assertEqual(PokemonFetcher._mega_item_name("mewtwo-mega-y"), "mewtwoite-y")


class FakePokemonMovesFetcher(PokemonMovesFetcher):
    def __init__(self, payloads: dict[str, dict[str, Any]]) -> None:
        super().__init__()
        self.payloads = payloads
        self.calls: list[str] = []

    def _get_json(self, path: str) -> dict[str, Any]:
        self.calls.append(path)
        return self.payloads[path]


class PokemonMovesFetcherTests(unittest.TestCase):
    def test_fetch_pokemon_moves_enriches_move_details(self) -> None:
        fetcher = FakePokemonMovesFetcher(
            {
                "pokemon/bulbasaur/": {
                    "id": 1,
                    "name": "bulbasaur",
                    "species": {"name": "bulbasaur"},
                    "stats": [
                        {"stat": {"name": "attack"}, "base_stat": 49},
                        {"stat": {"name": "special-attack"}, "base_stat": 65},
                    ],
                    "moves": [
                        {
                            "move": {"name": "vine-whip"},
                            "version_group_details": [{"level_learned_at": 3}],
                        }
                    ],
                },
                "move/vine-whip/": {
                    "id": 22,
                    "name": "vine-whip",
                    "accuracy": 100,
                    "effect_chance": None,
                    "pp": 25,
                    "priority": 0,
                    "power": 45,
                    "damage_class": {"name": "physical"},
                    "generation": {"name": "generation-i"},
                    "meta": {"category": {"name": "damage"}},
                    "stat_changes": [],
                    "target": {"name": "selected-pokemon"},
                    "type": {"name": "grass"},
                },
            }
        )

        result = fetcher.fetch_pokemon_moves("Bulbasaur", max_workers=1)

        self.assertEqual(fetcher.calls, ["pokemon/bulbasaur/", "move/vine-whip/"])
        self.assertEqual(result["pokemon"]["id"], 1)
        self.assertEqual(result["pokemon"]["name"], "bulbasaur")
        self.assertEqual(result["pokemon"]["species"]["name"], "bulbasaur")
        self.assertEqual(result["pokemon"]["stats"]["special-attack"], 65)
        move = result["moves"][0]
        self.assertEqual(move["move"]["name"], "vine-whip")
        self.assertEqual(move["version_group_details"][0]["level_learned_at"], 3)
        self.assertEqual(move["details"]["name"], "vine-whip")
        self.assertEqual(move["details"]["accuracy"], 100)
        self.assertEqual(move["details"]["power"], 45)
        self.assertEqual(move["details"]["damage_class"]["name"], "physical")
        self.assertEqual(move["details"]["type"]["name"], "grass")


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
