"""Tests for script-level Pokemon ranking helpers."""

from __future__ import annotations

import unittest
from typing import Any

from mcp_server.src.application.use_cases.rank_moveset import rank_moveset_data
from mcp_server.src.application.use_cases.rank_pokemon import rank_pokemon, score_pokemon


class FakePokemonFetcher:
    def __init__(self, pokemon: list[dict[str, Any]]) -> None:
        self.pokemon = pokemon
        self.calls: list[dict[str, Any]] = []

    def fetch_pokemon(
        self,
        types: list[str] | tuple[str, ...] | None = None,
        ability: str | None = None,
        move: str | None = None,
        max_workers: int = 12,
    ) -> list[dict[str, Any]]:
        self.calls.append(
            {
                "types": types,
                "ability": ability,
                "move": move,
                "max_workers": max_workers,
            }
        )
        return self.pokemon


class RankPokemonTests(unittest.TestCase):
    def test_score_uses_greater_offense_and_ignores_speed(self) -> None:
        result = score_pokemon(
            {
                "name": "alakazam",
                "stats": {
                    "hp": 55,
                    "attack": 50,
                    "defense": 45,
                    "special-attack": 135,
                    "special-defense": 95,
                    "speed": 120,
                },
            }
        )

        self.assertEqual(result["score"], 330)
        self.assertEqual(result["selected_offense_stat"], "special-attack")
        self.assertEqual(result["ignored_stats"], ["attack", "speed"])
        self.assertNotIn("speed", result["score_parts"])

    def test_rank_orders_by_score_descending_and_limits_head_size(self) -> None:
        fetcher = FakePokemonFetcher(
            [
                {
                    "name": "fast-low-total",
                    "stats": {
                        "hp": 10,
                        "attack": 10,
                        "defense": 10,
                        "special-attack": 10,
                        "special-defense": 10,
                        "speed": 255,
                    },
                },
                {
                    "name": "balanced-high",
                    "stats": {
                        "hp": 100,
                        "attack": 90,
                        "defense": 100,
                        "special-attack": 80,
                        "special-defense": 100,
                        "speed": 1,
                    },
                },
                {
                    "name": "special-high",
                    "stats": {
                        "hp": 70,
                        "attack": 40,
                        "defense": 80,
                        "special-attack": 150,
                        "special-defense": 90,
                        "speed": 10,
                    },
                },
            ]
        )

        result = rank_pokemon(
            fetcher,
            types=["grass", "null", "poison"],
            head_size=2,
            max_workers=3,
        )

        self.assertEqual([item["name"] for item in result], ["balanced-high", "special-high"])
        self.assertEqual([item["score"] for item in result], [390, 390])
        self.assertEqual(fetcher.calls[0]["types"], ["grass", "poison"])
        self.assertEqual(fetcher.calls[0]["max_workers"], 3)

    def test_score_preserves_mega_metadata(self) -> None:
        result = score_pokemon(
            {
                "name": "venusaur-mega",
                "stats": {
                    "hp": 80,
                    "attack": 100,
                    "defense": 123,
                    "special-attack": 122,
                    "special-defense": 120,
                    "speed": 80,
                },
                "is_mega": True,
                "is_battle_only": False,
                "base_pokemon": "venusaur",
                "required_item": {"name": "venusaurite"},
            }
        )

        self.assertTrue(result["is_mega"])
        self.assertFalse(result["is_battle_only"])
        self.assertEqual(result["base_pokemon"], "venusaur")
        self.assertEqual(result["required_item"]["name"], "venusaurite")

    def test_manual_offense_stat_forces_attack_or_special_attack(self) -> None:
        pokemon = {
            "name": "mixed",
            "stats": {
                "hp": 80,
                "attack": 120,
                "defense": 70,
                "special-attack": 30,
                "special-defense": 60,
                "speed": 200,
            },
        }

        attack_result = score_pokemon(pokemon, offense_stat="attack")
        special_result = score_pokemon(pokemon, offense_stat="special-attack")

        self.assertEqual(attack_result["score"], 330)
        self.assertEqual(special_result["score"], 240)
        self.assertEqual(special_result["ignored_stats"], ["attack", "speed"])

    def test_priority_stat_receives_multiplier(self) -> None:
        result = score_pokemon(
            {
                "name": "defensive",
                "stats": {
                    "hp": 80,
                    "attack": 120,
                    "defense": 70,
                    "special-attack": 30,
                    "special-defense": 60,
                    "speed": 200,
                },
            },
            priority_stat="defense",
        )

        self.assertEqual(result["score_parts"]["defense"], 70)
        self.assertEqual(result["weighted_score_parts"]["defense"], 98.0)
        self.assertEqual(result["score"], 358.0)
        self.assertEqual(result["priority_stat"], "defense")
        self.assertEqual(result["priority_multiplier"], 1.4)

    def test_speed_mode_can_prioritize_fast_or_slow_pokemon(self) -> None:
        fetcher = FakePokemonFetcher(
            [
                {
                    "name": "slow",
                    "stats": {
                        "hp": 10,
                        "attack": 10,
                        "defense": 10,
                        "special-attack": 10,
                        "special-defense": 10,
                        "speed": 5,
                    },
                },
                {
                    "name": "fast",
                    "stats": {
                        "hp": 10,
                        "attack": 10,
                        "defense": 10,
                        "special-attack": 10,
                        "special-defense": 10,
                        "speed": 200,
                    },
                },
            ]
        )

        fast_result = rank_pokemon(
            fetcher,
            priority_stat="speed",
            speed_mode="high",
            head_size=1,
        )
        slow_result = rank_pokemon(
            fetcher,
            priority_stat="speed",
            speed_mode="low",
            head_size=1,
        )

        self.assertEqual(fast_result[0]["name"], "fast")
        self.assertEqual(slow_result[0]["name"], "slow")
        self.assertEqual(slow_result[0]["score_parts"]["speed"], 250)


class RankMovesetTests(unittest.TestCase):
    def test_rank_moveset_uses_best_physical_attribute_and_appends_status(self) -> None:
        data = {
            "pokemon": {
                "id": 1,
                "name": "physical-mon",
                "stats": {"attack": 120, "special-attack": 80},
            },
            "moves": [
                self.move("status-one", None, None, "status"),
                self.move("physical-high-score", 90, 100, "physical"),
                self.move("special-ignored", 100, 200, "special"),
                self.move("physical-tie-accuracy", 100, 86, "physical"),
                self.move("status-two", None, None, "status"),
            ],
        }

        result = rank_moveset_data(data)

        self.assertEqual(result["selected_offense_stat"], "attack")
        self.assertEqual(result["selected_damage_class"], "physical")
        self.assertEqual(
            [move["name"] for move in result["moves"]],
            ["physical-tie-accuracy", "physical-high-score", "status-one", "status-two"],
        )
        self.assertEqual(result["moves"][0]["score"], 226.0)
        self.assertEqual(result["moves"][1]["score"], 226.0)
        self.assertEqual(result["moves"][2]["category"], "status")
        self.assertIsNone(result["moves"][2]["rank"])

    def test_rank_moveset_uses_special_attribute(self) -> None:
        data = {
            "pokemon": {
                "id": 2,
                "name": "special-mon",
                "stats": {"attack": 70, "special-attack": 130},
            },
            "moves": [
                self.move("physical-ignored", 100, 150, "physical"),
                self.move("special-ranked", 95, 80, "special"),
                self.move("special-better", 80, 120, "special"),
            ],
        }

        result = rank_moveset_data(data)

        self.assertEqual(result["selected_offense_stat"], "special-attack")
        self.assertEqual(result["selected_damage_class"], "special")
        self.assertEqual(
            [move["name"] for move in result["moves"]],
            ["special-better", "special-ranked"],
        )

    @staticmethod
    def move(
        name: str,
        accuracy: int | None,
        power: int | None,
        damage_class: str,
    ) -> dict[str, Any]:
        return {
            "move": {"name": name, "url": f"http://localhost/api/v2/move/{name}/"},
            "version_group_details": [],
            "details": {
                "name": name,
                "accuracy": accuracy,
                "power": power,
                "damage_class": {"name": damage_class},
                "type": {"name": "normal"},
                "pp": 10,
                "priority": 0,
            },
        }


if __name__ == "__main__":
    unittest.main()
