"""Tests for script-level Pokemon ranking helpers."""

from __future__ import annotations

import unittest
from typing import Any

from mcp_server.src.application.use_cases.champions_legality import (
    validate_champions_legality,
)
from mcp_server.src.application.use_cases.champions_strategy import search_champions_strategy
from mcp_server.src.application.use_cases.rank_moveset import rank_moveset_data
from mcp_server.src.application.use_cases.rank_pokemon import (
    has_required_stats,
    rank_pokemon,
    score_pokemon,
)


class FakePokemonFetcher:
    def __init__(self, pokemon: list[dict[str, Any]], fail_with: RuntimeError | None = None) -> None:
        self.pokemon = pokemon
        self.fail_with = fail_with
        self.calls: list[dict[str, Any]] = []

    def fetch_pokemon(
        self,
        types: list[str] | tuple[str, ...] | None = None,
        ability: str | None = None,
        move: str | None = None,
        champions_only: bool = False,
        allowed_species: set[str] | None = None,
        max_workers: int = 12,
    ) -> list[dict[str, Any]]:
        self.calls.append(
            {
                "types": types,
                "ability": ability,
                "move": move,
                "champions_only": champions_only,
                "allowed_species": allowed_species,
                "max_workers": max_workers,
            }
        )
        if self.fail_with is not None:
            raise self.fail_with
        return self.pokemon

    def fetch_pokemon_detail(
        self,
        pokemon: str | int,
        champions_only: bool = False,
        allowed_species: set[str] | None = None,
    ) -> dict[str, Any]:
        if self.fail_with is not None:
            raise self.fail_with
        for item in self.pokemon:
            if item["name"] == pokemon:
                return item
        raise RuntimeError("API request failed with HTTP 404")


class FakeMovesFetcher:
    def __init__(self, moves_by_pokemon: dict[str, list[str]]) -> None:
        self.moves_by_pokemon = moves_by_pokemon

    def fetch_pokemon_moves(self, pokemon: str | int, max_workers: int = 12) -> dict[str, Any]:
        moves = self.moves_by_pokemon.get(str(pokemon), [])
        return {
            "pokemon": {"name": str(pokemon), "stats": {"attack": 100, "special-attack": 100}},
            "moves": [{"move": {"name": move}, "details": {"name": move}} for move in moves],
        }


class FakeItemFetcher:
    def fetch_item(self, item: str | int) -> dict[str, Any]:
        return {
            "id": 1,
            "name": str(item),
            "category": {"name": "held-items"},
            "attributes": [{"name": "holdable"}],
            "effect_entries": [{"effect": "Boosts something.", "language": {"name": "en"}}],
        }


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

    def test_rank_excludes_pokemon_without_complete_stats(self) -> None:
        fetcher = FakePokemonFetcher(
            [
                {
                    "name": "archaludon",
                    "champions_dex": True,
                    "stats": {},
                },
                {
                    "name": "complete-mon",
                    "champions_dex": True,
                    "stats": {
                        "hp": 80,
                        "attack": 90,
                        "defense": 100,
                        "special-attack": 110,
                        "special-defense": 70,
                        "speed": 85,
                    },
                },
            ]
        )

        result = rank_pokemon(fetcher, champions_only=True, head_size=10)

        self.assertFalse(has_required_stats(fetcher.pokemon[0]))
        self.assertEqual([pokemon["name"] for pokemon in result], ["complete-mon"])


    def test_rank_can_request_champions_scope(self) -> None:
        fetcher = FakePokemonFetcher(
            [
                {
                    "name": "venusaur",
                    "champions_dex": True,
                    "species": {"name": "venusaur"},
                    "stats": {
                        "hp": 80,
                        "attack": 82,
                        "defense": 83,
                        "special-attack": 100,
                        "special-defense": 100,
                        "speed": 80,
                    },
                }
            ]
        )

        result = rank_pokemon(
            fetcher,
            champions_only=True,
            allowed_species={"venusaur"},
            head_size=1,
        )

        self.assertEqual(result[0]["name"], "venusaur")
        self.assertTrue(result[0]["champions_dex"])
        self.assertTrue(fetcher.calls[0]["champions_only"])
        self.assertEqual(fetcher.calls[0]["allowed_species"], {"venusaur"})

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

    def test_rank_moveset_rejects_missing_offense_stats(self) -> None:
        data = {
            "pokemon": {
                "id": 1018,
                "name": "archaludon",
                "stats": {},
            },
            "moves": [self.move("flash-cannon", 100, 80, "special")],
        }

        with self.assertRaisesRegex(RuntimeError, "stats ofensivos incompletos"):
            rank_moveset_data(data)

    def test_rank_moveset_rejects_empty_move_list(self) -> None:
        data = {
            "pokemon": {
                "id": 1018,
                "name": "archaludon",
                "stats": {"attack": 105, "special-attack": 125},
            },
            "moves": [],
        }

        with self.assertRaisesRegex(RuntimeError, "Nenhum golpe encontrado"):
            rank_moveset_data(data)

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


class ChampionsLegalityTests(unittest.TestCase):
    def test_validates_champions_pokemon_legality(self) -> None:
        result = validate_champions_legality(
            "pokemon",
            "archaludon",
            pokemon_fetcher=FakePokemonFetcher([complete_pokemon("archaludon")]),
        )

        self.assertTrue(result["eligible"])
        self.assertTrue(result["legal"])
        self.assertEqual(result["facts"]["pokemon"]["name"], "archaludon")
        self.assertEqual(result["diagnostics"], [])

    def test_reports_outside_champions_scope(self) -> None:
        pokemon = complete_pokemon("pelipper")
        pokemon["champions_dex"] = False

        result = validate_champions_legality(
            "pokemon",
            "pelipper",
            pokemon_fetcher=FakePokemonFetcher([pokemon]),
        )

        self.assertFalse(result["eligible"])
        self.assertEqual(result["diagnostics"][0]["code"], "outside_champions_scope")

    def test_validates_move_and_ability(self) -> None:
        result = validate_champions_legality(
            "move",
            "rain-dance",
            pokemon="pelipper",
            pokemon_fetcher=FakePokemonFetcher([complete_pokemon("pelipper")]),
            moves_fetcher=FakeMovesFetcher({"pelipper": ["rain-dance", "hurricane"]}),
        )
        ability = validate_champions_legality(
            "ability",
            "drizzle",
            pokemon="pelipper",
            pokemon_fetcher=FakePokemonFetcher([complete_pokemon("pelipper", abilities=["drizzle"])]),
        )

        self.assertTrue(result["legal"])
        self.assertTrue(result["facts"]["move"]["learned_by_pokemon"])
        self.assertTrue(ability["legal"])
        self.assertTrue(ability["facts"]["ability"]["known_for_pokemon"])

    def test_item_legality_reports_unsupported_champions_dimension(self) -> None:
        result = validate_champions_legality(
            "item",
            "damp-rock",
            pokemon_fetcher=FakePokemonFetcher([]),
            item_fetcher=FakeItemFetcher(),
        )

        self.assertTrue(result["eligible"])
        self.assertFalse(result["legal"])
        self.assertEqual(result["diagnostics"][0]["code"], "unsupported_validation")

    def test_focused_validation_reports_source_timeout(self) -> None:
        result = validate_champions_legality(
            "pokemon",
            "archaludon",
            pokemon_fetcher=FakePokemonFetcher([], fail_with=RuntimeError("source timeout")),
        )

        self.assertFalse(result["eligible"])
        self.assertEqual(result["diagnostics"][0]["code"], "source_unavailable")


class ChampionsStrategyTests(unittest.TestCase):
    def test_searches_rain_setter_and_rain_attacker(self) -> None:
        fetcher = FakePokemonFetcher(
            [
                complete_pokemon("pelipper", types=["water", "flying"], abilities=["drizzle"]),
                complete_pokemon("archaludon", types=["steel", "dragon"], abilities=["stamina"]),
                complete_pokemon("barraskewda", types=["water"], abilities=["swift-swim"]),
            ]
        )

        setters = search_champions_strategy("rain-setter", fetcher=fetcher)
        attackers = search_champions_strategy("rain-attacker", fetcher=fetcher)

        self.assertEqual(setters["candidates"][0]["pokemon"]["name"], "pelipper")
        self.assertEqual(setters["candidates"][0]["evidence"][0]["name"], "drizzle")
        self.assertIn(
            "barraskewda",
            [candidate["pokemon"]["name"] for candidate in attackers["candidates"]],
        )

    def test_rain_setter_uses_role_specific_filters_before_fallback(self) -> None:
        fetcher = FakePokemonFetcher(
            [
                complete_pokemon("pelipper", types=["water", "flying"], abilities=["drizzle"]),
            ]
        )

        result = search_champions_strategy("rain-setter", fetcher=fetcher)

        self.assertEqual(result["candidates"][0]["pokemon"]["name"], "pelipper")
        self.assertIn({"types": None, "ability": "drizzle", "move": None, "champions_only": True, "allowed_species": None, "max_workers": 4}, fetcher.calls)
        self.assertIn({"types": None, "ability": None, "move": "rain-dance", "champions_only": True, "allowed_species": None, "max_workers": 4}, fetcher.calls)
        self.assertNotIn({"types": None, "ability": None, "move": None, "champions_only": True, "allowed_species": None, "max_workers": 4}, fetcher.calls)

    def test_injected_rain_setter_case_uses_ability_and_move_evidence(self) -> None:
        fetcher = FakePokemonFetcher(
            [
                complete_pokemon("pelipper", types=["water", "flying"], abilities=["drizzle"]),
                complete_pokemon(
                    "rotom-wash",
                    types=["electric", "water"],
                    abilities=["levitate"],
                    moves=[{"name": "rain-dance"}],
                ),
            ]
        )

        result = search_champions_strategy(
            case={
                "name": "custom-rain-setter",
                "queries": [
                    {"source": "ability", "ability": "drizzle"},
                    {"source": "move", "move": "rain-dance"},
                ],
                "evidence": {
                    "any": [
                        {"kind": "ability", "name": "drizzle"},
                        {"kind": "move", "name": "rain-dance"},
                    ]
                },
            },
            fetcher=fetcher,
        )

        self.assertIsNone(result["role"])
        self.assertEqual(result["case_name"], "custom-rain-setter")
        self.assertEqual(
            [candidate["pokemon"]["name"] for candidate in result["candidates"]],
            ["pelipper", "rotom-wash"],
        )
        self.assertEqual(result["case"]["evidence"]["any"][0]["name"], "drizzle")

    def test_injected_non_weather_case_uses_type_and_stat_evidence(self) -> None:
        fetcher = FakePokemonFetcher(
            [
                complete_pokemon(
                    "archaludon",
                    types=["steel", "dragon"],
                    stats={"hp": 90, "attack": 105, "defense": 130, "special-attack": 125, "special-defense": 65, "speed": 85},
                ),
                complete_pokemon("klefki", types=["steel", "fairy"], stats={"hp": 57, "attack": 80, "defense": 91, "special-attack": 80, "special-defense": 87, "speed": 75}),
            ]
        )

        result = search_champions_strategy(
            case={
                "name": "steel-special-breaker",
                "queries": [{"source": "types", "types": ["steel"]}],
                "evidence": {
                    "any": [
                        {"kind": "type", "name": "steel"},
                        {"kind": "stat_profile", "name": "strong-special", "stat": "special-attack", "min": 120},
                    ]
                },
            },
            fetcher=fetcher,
        )

        self.assertEqual(result["case_name"], "steel-special-breaker")
        self.assertIn("archaludon", [candidate["pokemon"]["name"] for candidate in result["candidates"]])
        archaludon = result["candidates"][0]
        self.assertIn(
            {"kind": "stat_profile", "name": "strong-special", "value": 125},
            archaludon["evidence"],
        )

    def test_predefined_roles_remain_builtin_cases(self) -> None:
        fetcher = FakePokemonFetcher(
            [
                complete_pokemon("pelipper", types=["water", "flying"], abilities=["drizzle"]),
                complete_pokemon("archaludon", types=["steel", "dragon"], abilities=["stamina"]),
            ]
        )

        result = search_champions_strategy("rain-setter", fetcher=fetcher)

        self.assertEqual(result["role"], "rain-setter")
        self.assertNotIn("case", result)
        self.assertEqual(result["candidates"][0]["pokemon"]["name"], "pelipper")

    def test_injected_case_validation_errors_are_structured(self) -> None:
        fetcher = FakePokemonFetcher([])

        with self.assertRaisesRegex(ValueError, "role ou case"):
            search_champions_strategy("rain-setter", case={"name": "x"}, fetcher=fetcher)

        with self.assertRaisesRegex(ValueError, "query"):
            search_champions_strategy(case={"name": "x", "evidence": {"any": [{"kind": "type", "name": "water"}]}}, fetcher=fetcher)

        with self.assertRaisesRegex(ValueError, "Fonte de query"):
            search_champions_strategy(
                case={
                    "name": "x",
                    "queries": [{"source": "sql", "statement": "select *"}],
                    "evidence": {"any": [{"kind": "type", "name": "water"}]},
                },
                fetcher=fetcher,
            )

    def test_broad_fallback_is_capped_and_reports_partial_results(self) -> None:
        result = search_champions_strategy(
            "speed-control",
            fetcher=FakePokemonFetcher([]),
            candidate_scan_limit=2,
        )

        self.assertTrue(result["partial_results"])
        self.assertEqual(result["candidate_count"], 0)
        self.assertEqual(result["diagnostics"][0]["code"], "strategy_search_budget_exhausted")

    def test_strategy_search_excludes_unproven_champions_membership(self) -> None:
        candidate = complete_pokemon("pelipper", abilities=["drizzle"])
        candidate["champions_dex"] = None

        result = search_champions_strategy(
            "rain-setter",
            fetcher=FakePokemonFetcher([candidate]),
        )

        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["excluded_count"], 1)
        self.assertEqual(result["excluded"][0]["reason"], "champions_dex_not_true")

    def test_strategy_search_reports_no_candidates(self) -> None:
        result = search_champions_strategy(
            "rain-setter",
            fetcher=FakePokemonFetcher([complete_pokemon("archaludon")]),
        )

        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["diagnostics"][0]["code"], "no_eligible_candidates")

    def test_archaludon_rain_path_has_six_champions_candidates(self) -> None:
        fetcher = FakePokemonFetcher(archaludon_rain_candidates())

        roles = [
            "rain-setter",
            "rain-attacker",
            "defensive-pivot",
            "ground-check",
            "speed-control",
            "win-condition",
        ]
        results = {
            role: search_champions_strategy(role, fetcher=fetcher)
            for role in roles
        }

        self.assertTrue(all(result["candidates"] for result in results.values()))
        names = {
            candidate["pokemon"]["name"]
            for result in results.values()
            for candidate in result["candidates"]
        }
        self.assertIn("archaludon", names)
        self.assertGreaterEqual(len(names), 6)


def complete_pokemon(
    name: str,
    *,
    types: list[str] | None = None,
    abilities: list[str] | None = None,
    stats: dict[str, int] | None = None,
    moves: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    data = {
        "id": len(name),
        "name": name,
        "species": {"name": name},
        "types": types or ["dragon"],
        "abilities": [{"name": ability, "is_hidden": False, "slot": index + 1} for index, ability in enumerate(abilities or ["stamina"])],
        "stats": stats
        or {
            "hp": 90,
            "attack": 100,
            "defense": 100,
            "special-attack": 120,
            "special-defense": 80,
            "speed": 85,
        },
        "champions_dex": True,
        "complete": True,
        "eligible": True,
        "is_legendary": False,
        "is_battle_only": False,
    }
    if moves is not None:
        data["moves"] = moves
    return data


def archaludon_rain_candidates() -> list[dict[str, Any]]:
    return [
        complete_pokemon("archaludon", types=["steel", "dragon"], stats={"hp": 90, "attack": 105, "defense": 130, "special-attack": 125, "special-defense": 65, "speed": 85}),
        complete_pokemon("pelipper", types=["water", "flying"], abilities=["drizzle"], stats={"hp": 60, "attack": 50, "defense": 100, "special-attack": 95, "special-defense": 70, "speed": 65}),
        complete_pokemon("barraskewda", types=["water"], abilities=["swift-swim"], stats={"hp": 61, "attack": 123, "defense": 60, "special-attack": 60, "special-defense": 50, "speed": 136}),
        complete_pokemon("rotom-wash", types=["electric", "water"], stats={"hp": 50, "attack": 65, "defense": 107, "special-attack": 105, "special-defense": 107, "speed": 86}),
        complete_pokemon("amoonguss", types=["grass", "poison"], stats={"hp": 114, "attack": 85, "defense": 70, "special-attack": 85, "special-defense": 80, "speed": 30}),
        complete_pokemon("tornadus", types=["flying"], stats={"hp": 79, "attack": 100, "defense": 80, "special-attack": 110, "special-defense": 90, "speed": 121}),
    ]


if __name__ == "__main__":
    unittest.main()
