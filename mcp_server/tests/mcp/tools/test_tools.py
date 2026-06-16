"""Tests for AI tool wrappers."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from typing import Any

from mcp_server.src.mcp.tools import (
    BAN_POKEMON_TOOL,
    CHAMPIONS_LEGALITY_TOOL,
    ITEM_TOOL,
    POKEMON_MOVESET_TOOL,
    POKEMON_RANKING_TOOL,
    TYPE_RELATIONS_TOOL,
    execute_ban_pokemon_tool,
    execute_champions_legality_tool,
    execute_item_tool,
    execute_pokemon_moveset_tool,
    execute_pokemon_ranking_tool,
    execute_type_relations_tool,
)
from mcp_server.src.mcp import server
from mcp_server.src.mcp.server import call_tool, handle_message, tool_definition, tool_definitions


class BanPokemonToolTests(unittest.TestCase):
    def test_tool_schema_requires_id_and_name_arguments(self) -> None:
        function = BAN_POKEMON_TOOL["function"]

        self.assertEqual(function["name"], "ban_pokemon")
        self.assertEqual(function["parameters"]["required"], ["id", "name"])
        self.assertIn("id", function["parameters"]["properties"])
        self.assertIn("name", function["parameters"]["properties"])

    def test_execute_tool_adds_pokemon_to_sqlite_database(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "banned_pokemon.sqlite3"

            result = execute_ban_pokemon_tool(
                {"id": 6, "name": " Charizard "},
                db_path=db_path,
            )

            with sqlite3.connect(db_path) as connection:
                rows = connection.execute(
                    "SELECT id, name FROM banned_pokemon"
                ).fetchall()

        self.assertEqual(result["tool_name"], "ban_pokemon")
        self.assertEqual(result["input"], {"id": 6, "name": "charizard"})
        self.assertTrue(result["data"]["created"])
        self.assertEqual(rows, [(6, "charizard")])
        self.assertIn("Pokemon proibido: charizard", result["presentation"])

    def test_execute_tool_does_not_duplicate_existing_pokemon(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "banned_pokemon.sqlite3"
            execute_ban_pokemon_tool({"id": 6, "name": "charizard"}, db_path=db_path)

            result = execute_ban_pokemon_tool(
                {"id": 6, "name": "charizard"},
                db_path=db_path,
            )

            with sqlite3.connect(db_path) as connection:
                count = connection.execute(
                    "SELECT count(*) FROM banned_pokemon"
                ).fetchone()[0]

        self.assertFalse(result["data"]["created"])
        self.assertEqual(count, 1)

    def test_execute_tool_validates_arguments(self) -> None:
        with self.assertRaises(ValueError):
            execute_ban_pokemon_tool({"id": 0, "name": "mewtwo"})

        with self.assertRaises(ValueError):
            execute_ban_pokemon_tool({"id": 150, "name": ""})


class ItemToolTests(unittest.TestCase):
    def test_tool_schema_accepts_pagination_arguments(self) -> None:
        function = ITEM_TOOL["function"]

        self.assertEqual(function["name"], "list_items")
        self.assertNotIn("required", function["parameters"])
        self.assertIn("limit", function["parameters"]["properties"])
        self.assertIn("offset", function["parameters"]["properties"])

    def test_execute_tool_returns_data_and_presentation(self) -> None:
        result = execute_item_tool(
            {"limit": 1, "offset": 0},
            fetcher=self.fake_fetcher,
        )

        self.assertEqual(result["tool_name"], "list_items")
        self.assertEqual(result["input"], {"limit": 1, "offset": 0})
        self.assertEqual(result["data"]["items"][0]["name"], "oran-berry")
        item = result["data"]["items"][0]
        self.assertEqual(result["data"]["count"], 2)
        self.assertEqual(result["data"]["limit"], 1)
        self.assertEqual(result["data"]["offset"], 0)
        self.assertEqual(item["category"]["name"], "medicine")
        self.assertEqual(item["cost"], 80)
        self.assertEqual(item["fling_power"], 10)
        self.assertEqual(item["fling_effect"]["name"], "berry-effect")
        self.assertEqual(item["attributes"][0]["name"], "holdable")
        self.assertEqual(item["effect_entries"][1]["effect"], "Restores 10 HP.")
        self.assertEqual(item["flavor_text_entries"][0]["text"], "A berry.")
        self.assertEqual(item["sprites"]["default"], "item.png")
        self.assertIn("Itens encontrados: 1", result["presentation"])
        self.assertIn("oran-berry", result["presentation"])
        self.assertIn("Restores 10 HP.", result["presentation"])

    def test_execute_tool_validates_arguments(self) -> None:
        with self.assertRaises(ValueError):
            execute_item_tool({"limit": 0}, fetcher=self.fake_fetcher)

        with self.assertRaises(ValueError):
            execute_item_tool({"limit": 101}, fetcher=self.fake_fetcher)

        with self.assertRaises(ValueError):
            execute_item_tool({"offset": -1}, fetcher=self.fake_fetcher)

    @staticmethod
    def fake_fetcher(limit: int, offset: int) -> dict[str, Any]:
        return {
            "count": 2,
            "next": None,
            "previous": None,
            "limit": limit,
            "offset": offset,
            "items": [
                {
                    "id": 132,
                    "name": "oran-berry",
                    "cost": 80,
                    "fling_power": 10,
                    "fling_effect": {"name": "berry-effect"},
                    "attributes": [{"name": "holdable"}],
                    "category": {"name": "medicine"},
                    "effect_entries": [
                        {
                            "effect": "Restaura 10 HP.",
                            "language": {"name": "pt-BR"},
                        },
                        {
                            "effect": "Restores 10 HP.",
                            "language": {"name": "en"},
                        },
                    ],
                    "flavor_text_entries": [{"text": "A berry.", "language": {"name": "en"}}],
                    "sprites": {"default": "item.png"},
                }
            ],
        }


class ChampionsLegalityToolTests(unittest.TestCase):
    def test_tool_schema_requires_entity_type_and_entity(self) -> None:
        function = CHAMPIONS_LEGALITY_TOOL["function"]

        self.assertEqual(function["name"], "validate_champions_legality")
        self.assertEqual(function["parameters"]["required"], ["entity_type", "entity"])
        self.assertIn("pokemon", function["parameters"]["properties"])

    def test_execute_tool_returns_structured_legality(self) -> None:
        result = execute_champions_legality_tool(
            {"entity_type": "pokemon", "entity": "archaludon"},
            validator=lambda entity_type, entity, pokemon: {
                "entity_type": entity_type,
                "entity": entity,
                "checked_scope": "pokemon_champions",
                "legal": True,
                "eligible": True,
                "facts": {"pokemon": {"name": "archaludon"}},
                "diagnostics": [],
                "blocking": False,
            },
        )

        self.assertEqual(result["tool_name"], "validate_champions_legality")
        self.assertEqual(result["input"]["entity"], "archaludon")
        self.assertTrue(result["data"]["eligible"])
        self.assertEqual(result["diagnostics"], [])
        self.assertIn("Elegivel: True", result["presentation"])

    def test_execute_tool_returns_diagnostics(self) -> None:
        result = execute_champions_legality_tool(
            {"entity_type": "pokemon", "entity": "missing"},
            validator=lambda entity_type, entity, pokemon: {
                "entity_type": entity_type,
                "entity": entity,
                "checked_scope": "pokemon_champions",
                "legal": False,
                "eligible": False,
                "facts": {},
                "diagnostics": [{"code": "pokemon_not_found", "message": "missing", "blocking": True}],
                "blocking": True,
            },
        )

        self.assertEqual(result["diagnostics"][0]["code"], "pokemon_not_found")
        self.assertIn("pokemon_not_found", result["presentation"])


class PokemonMovesetToolTests(unittest.TestCase):
    def test_tool_schema_requires_pokemon_argument(self) -> None:
        function = POKEMON_MOVESET_TOOL["function"]

        self.assertEqual(function["name"], "rank_pokemon_moveset")
        self.assertEqual(function["parameters"]["required"], ["pokemon"])
        self.assertIn("pokemon", function["parameters"]["properties"])

    def test_execute_tool_returns_data_and_presentation(self) -> None:
        result = execute_pokemon_moveset_tool(
            {"pokemon": "bulbasaur", "max_moves": 1},
            ranker=self.fake_ranker,
        )

        self.assertEqual(result["tool_name"], "rank_pokemon_moveset")
        self.assertEqual(result["input"], {"pokemon": "bulbasaur", "max_moves": 1})
        self.assertEqual(result["data"]["pokemon"]["name"], "bulbasaur")
        self.assertEqual(result["data"]["pokemon"]["id"], 1)
        self.assertEqual(result["data"]["pokemon"]["stats"]["special-attack"], 65)
        move = result["data"]["moves"][0]
        self.assertEqual(move["name"], "petal-dance")
        self.assertEqual(move["category"], "ranked")
        self.assertEqual(move["rank"], 1)
        self.assertEqual(move["score"], 260.0)
        self.assertEqual(move["accuracy"], 100)
        self.assertEqual(move["power"], 120)
        self.assertEqual(move["damage_class"], "special")
        self.assertEqual(move["type"], "grass")
        self.assertEqual(move["pp"], 10)
        self.assertEqual(move["priority"], 0)
        self.assertEqual(move["version_group_details"][0]["level_learned_at"], 0)
        self.assertIn("Pokemon: bulbasaur", result["presentation"])
        self.assertIn("#1 petal-dance", result["presentation"])
        self.assertNotIn("#2 solar-beam", result["presentation"])
        self.assertIn("Golpes de status listados ao fim: 1", result["presentation"])

    def test_execute_tool_validates_arguments(self) -> None:
        with self.assertRaises(ValueError):
            execute_pokemon_moveset_tool({}, ranker=self.fake_ranker)

        with self.assertRaises(ValueError):
            execute_pokemon_moveset_tool({"pokemon": "pikachu", "max_moves": 0}, ranker=self.fake_ranker)

    @staticmethod
    def fake_ranker(pokemon: str | int) -> dict[str, Any]:
        return {
            "pokemon": {
                "id": 1,
                "name": str(pokemon),
                "stats": {"attack": 49, "special-attack": 65},
            },
            "selected_offense_stat": "special-attack",
            "selected_damage_class": "special",
            "ranking_rule": "accuracy * 1.4 + power",
            "moves": [
                {
                    "rank": 1,
                    "name": "petal-dance",
                    "category": "ranked",
                    "score": 260.0,
                    "accuracy": 100,
                    "power": 120,
                    "damage_class": "special",
                    "type": "grass",
                    "pp": 10,
                    "priority": 0,
                    "version_group_details": [{"level_learned_at": 0}],
                },
                {
                    "rank": 2,
                    "name": "solar-beam",
                    "category": "ranked",
                    "score": 260.0,
                    "accuracy": 100,
                    "power": 120,
                    "damage_class": "special",
                    "type": "grass",
                    "pp": 10,
                    "priority": 0,
                    "version_group_details": [],
                },
                {
                    "rank": None,
                    "name": "sleep-powder",
                    "category": "status",
                    "score": None,
                    "accuracy": 75,
                    "power": None,
                    "damage_class": "status",
                    "type": "grass",
                    "pp": 15,
                    "priority": 0,
                    "version_group_details": [],
                },
            ],
        }


class PokemonRankingToolTests(unittest.TestCase):
    def test_tool_schema_accepts_optional_ranking_filters(self) -> None:
        function = POKEMON_RANKING_TOOL["function"]

        self.assertEqual(function["name"], "rank_pokemon")
        self.assertNotIn("required", function["parameters"])
        self.assertIn("types", function["parameters"]["properties"])
        self.assertIn("offense_stat", function["parameters"]["properties"])
        self.assertIn("priority_stat", function["parameters"]["properties"])
        self.assertIn("speed_mode", function["parameters"]["properties"])
        self.assertIn("head_size", function["parameters"]["properties"])
        self.assertIn("champions_only", function["parameters"]["properties"])
        self.assertEqual(
            function["parameters"]["properties"]["champions_only"]["type"],
            "boolean",
        )

    def test_execute_tool_returns_data_and_presentation(self) -> None:
        result = execute_pokemon_ranking_tool(
            {
                "types": ["grass", "poison"],
                "offense_stat": "auto",
                "priority_stat": "special-defense",
                "speed_mode": "high",
                "head_size": 1,
            },
            ranker=self.fake_ranker,
        )

        self.assertEqual(result["tool_name"], "rank_pokemon")
        self.assertEqual(
            result["input"],
            {
                "types": ["grass", "poison"],
                "offense_stat": "auto",
                "priority_stat": "special-defense",
                "speed_mode": "high",
                "head_size": 1,
                "champions_only": True,
            },
        )
        self.assertEqual(result["data"][0]["name"], "venusaur")
        pokemon = result["data"][0]
        self.assertEqual(pokemon["id"], 3)
        self.assertEqual(pokemon["stats"]["special-attack"], 100)
        self.assertEqual(pokemon["selected_offense_stat"], "special-attack")
        self.assertEqual(pokemon["score_parts"]["hp"], 80)
        self.assertEqual(pokemon["weighted_score_parts"]["special-defense"], 140.0)
        self.assertEqual(pokemon["species"]["name"], "venusaur")
        self.assertTrue(pokemon["champions_dex"])
        self.assertIn("Filtro de tipos: grass, poison", result["presentation"])
        self.assertIn("#1 venusaur", result["presentation"])
        self.assertIn("Escopo Champions: ativado", result["presentation"])
        self.assertNotIn("mega_item=", result["presentation"])

    def test_execute_tool_filters_banned_pokemon_from_sqlite(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "banned_pokemon.sqlite3"
            with sqlite3.connect(db_path) as connection:
                connection.execute("CREATE TABLE banned_pokemon (id INTEGER, name TEXT)")
                connection.executemany(
                    "INSERT INTO banned_pokemon (id, name) VALUES (?, ?)",
                    [(3, "venusaur"), (6, "charizard")],
                )

            result = execute_pokemon_ranking_tool(
                {"head_size": 3},
                ranker=self.fake_ranker_with_banned_entries,
                banned_db_path=db_path,
            )

        self.assertEqual([pokemon["name"] for pokemon in result["data"]], ["blastoise"])
        self.assertNotIn("venusaur", result["presentation"])
        self.assertNotIn("charizard", result["presentation"])
        self.assertIn("#1 blastoise", result["presentation"])

    def test_execute_tool_validates_arguments(self) -> None:
        with self.assertRaises(ValueError):
            execute_pokemon_ranking_tool({"types": "grass"}, ranker=self.fake_ranker)

        with self.assertRaises(ValueError):
            execute_pokemon_ranking_tool(
                {"types": ["fire", "flying", "dragon"]},
                ranker=self.fake_ranker,
            )

        with self.assertRaises(ValueError):
            execute_pokemon_ranking_tool({"offense_stat": "speed"}, ranker=self.fake_ranker)

        with self.assertRaises(ValueError):
            execute_pokemon_ranking_tool({"priority_stat": "evasion"}, ranker=self.fake_ranker)

        with self.assertRaises(ValueError):
            execute_pokemon_ranking_tool({"speed_mode": "middle"}, ranker=self.fake_ranker)

        with self.assertRaises(ValueError):
            execute_pokemon_ranking_tool({"head_size": 0}, ranker=self.fake_ranker)

        with self.assertRaises(ValueError):
            execute_pokemon_ranking_tool({"champions_only": "false"}, ranker=self.fake_ranker)

    def test_execute_tool_accepts_champions_scope_flag(self) -> None:
        calls = []

        def ranker(
            types: list[str] | None,
            offense_stat: str,
            priority_stat: str | None,
            speed_mode: str,
            head_size: int,
            champions_only: bool,
        ) -> list[dict[str, Any]]:
            calls.append(champions_only)
            return self.fake_ranker(
                types,
                offense_stat,
                priority_stat,
                speed_mode,
                head_size,
                champions_only,
            )

        result = execute_pokemon_ranking_tool(
            {"champions_only": False},
            ranker=ranker,
        )

        self.assertEqual(calls, [False])
        self.assertFalse(result["input"]["champions_only"])
        self.assertIn("Escopo Champions: desativado", result["presentation"])

    @staticmethod
    def fake_ranker(
        types: list[str] | None,
        offense_stat: str,
        priority_stat: str | None,
        speed_mode: str,
        head_size: int,
        champions_only: bool,
    ) -> list[dict[str, Any]]:
        return [
            {
                "id": 3,
                "name": "venusaur",
                "score": 363,
                "is_mega": False,
                "is_battle_only": False,
                "selected_offense_stat": "special-attack",
                "priority_stat": priority_stat,
                "priority_multiplier": 1.4 if priority_stat else None,
                "speed_mode": speed_mode,
                "ignored_stats": ["attack"],
                "score_parts": {
                    "hp": 80,
                    "defense": 83,
                    "special-defense": 100,
                    "special-attack": 100,
                    "speed": 80 if speed_mode != "ignore" else None,
                },
                "weighted_score_parts": {
                    "hp": 80,
                    "defense": 83,
                    "special-defense": 140.0 if priority_stat == "special-defense" else 100,
                    "special-attack": 100,
                    "speed": 80 if speed_mode != "ignore" else None,
                },
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
        ][:head_size]

    @staticmethod
    def fake_ranker_with_banned_entries(
        types: list[str] | None,
        offense_stat: str,
        priority_stat: str | None,
        speed_mode: str,
        head_size: int,
        champions_only: bool,
    ) -> list[dict[str, Any]]:
        return [
            make_ranked_pokemon(3, "venusaur", priority_stat, speed_mode),
            make_ranked_pokemon(9, "blastoise", priority_stat, speed_mode),
            make_ranked_pokemon(25, "charizard", priority_stat, speed_mode),
        ][:head_size]


def make_ranked_pokemon(
    pokemon_id: int,
    name: str,
    priority_stat: str | None,
    speed_mode: str,
) -> dict[str, Any]:
    return {
        "id": pokemon_id,
        "name": name,
        "score": 363,
        "is_mega": False,
        "is_battle_only": False,
        "selected_offense_stat": "attack",
        "priority_stat": priority_stat,
        "priority_multiplier": 1.4 if priority_stat else None,
        "speed_mode": speed_mode,
        "ignored_stats": ["special-attack"],
        "score_parts": {
            "hp": 80,
            "defense": 83,
            "special-defense": 100,
            "attack": 100,
            "speed": 80 if speed_mode != "ignore" else None,
        },
        "weighted_score_parts": {
            "hp": 80,
            "defense": 83,
            "special-defense": 100,
            "attack": 100,
            "speed": 80 if speed_mode != "ignore" else None,
        },
        "stats": {
            "hp": 80,
            "attack": 100,
            "defense": 83,
            "special-attack": 82,
            "special-defense": 100,
            "speed": 80,
        },
    }


class TypeRelationsToolTests(unittest.TestCase):
    def test_tool_schema_requires_type_argument(self) -> None:
        function = TYPE_RELATIONS_TOOL["function"]

        self.assertEqual(function["name"], "get_type_relations")
        self.assertEqual(function["parameters"]["required"], ["type"])
        self.assertIn("type", function["parameters"]["properties"])

    def test_execute_tool_returns_data_and_presentation(self) -> None:
        result = execute_type_relations_tool(
            {"type": "fire"},
            fetcher=self.fake_fetcher,
        )

        self.assertEqual(result["tool_name"], "get_type_relations")
        self.assertEqual(result["input"], {"type": "fire"})
        self.assertEqual(result["data"]["type"]["name"], "fire")
        self.assertEqual(result["data"]["type"]["id"], 10)
        self.assertEqual(result["data"]["offensive"]["super_effective_against"], ["grass", "ice"])
        self.assertEqual(result["data"]["offensive"]["weak_against"], ["water"])
        self.assertEqual(result["data"]["offensive"]["no_effect_against"], [])
        self.assertEqual(result["data"]["defensive"]["weak_to"], ["water", "rock"])
        self.assertEqual(result["data"]["defensive"]["resists"], ["fire", "grass"])
        self.assertEqual(result["data"]["defensive"]["immune_to"], [])
        self.assertIn("Tipo: fire", result["presentation"])
        self.assertIn("Superefetivo contra: grass, ice", result["presentation"])
        self.assertIn("Sofre superefetivo de: water, rock", result["presentation"])

    def test_execute_tool_validates_arguments(self) -> None:
        with self.assertRaises(ValueError):
            execute_type_relations_tool({}, fetcher=self.fake_fetcher)

        with self.assertRaises(ValueError):
            execute_type_relations_tool({"type": ""}, fetcher=self.fake_fetcher)

    @staticmethod
    def fake_fetcher(pokemon_type: str | int) -> dict[str, Any]:
        return {
            "type": {"id": 10, "name": str(pokemon_type)},
            "offensive": {
                "super_effective_against": ["grass", "ice"],
                "weak_against": ["water"],
                "no_effect_against": [],
            },
            "defensive": {
                "weak_to": ["water", "rock"],
                "resists": ["fire", "grass"],
                "immune_to": [],
            },
            "raw_damage_relations": {},
        }


class PokemonMcpServerTests(unittest.TestCase):
    def test_initialize_and_tools_list(self) -> None:
        initialize = handle_message(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "test-version"},
            }
        )
        tools = handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})

        self.assertEqual(initialize["result"]["protocolVersion"], "test-version")
        self.assertEqual(tools["result"]["tools"], tool_definitions())
        self.assertIn(tool_definition(BAN_POKEMON_TOOL), tools["result"]["tools"])
        self.assertIn(tool_definition(CHAMPIONS_LEGALITY_TOOL), tools["result"]["tools"])
        self.assertIn(tool_definition(ITEM_TOOL), tools["result"]["tools"])
        self.assertIn(tool_definition(POKEMON_MOVESET_TOOL), tools["result"]["tools"])
        self.assertIn(tool_definition(POKEMON_RANKING_TOOL), tools["result"]["tools"])
        self.assertIn(tool_definition(TYPE_RELATIONS_TOOL), tools["result"]["tools"])
        tool_names = {tool["name"] for tool in tools["result"]["tools"]}
        self.assertNotIn("build_pokemon_team", tool_names)
        self.assertNotIn("search_champions_strategy", tool_names)


    def test_team_builder_tool_dispatch_returns_unknown_tool_error(self) -> None:
        response = handle_message(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "build_pokemon_team", "arguments": {"pokemon": ["pikachu"]}},
            }
        )

        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("Tool desconhecida: build_pokemon_team", response["error"]["message"])

    def test_champions_strategy_tool_dispatch_returns_unknown_tool_error(self) -> None:
        response = handle_message(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "search_champions_strategy", "arguments": {"role": "rain-setter"}},
            }
        )

        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("Tool desconhecida: search_champions_strategy", response["error"]["message"])

    def test_tool_call_preserves_full_structured_content(self) -> None:
        original_tools = server.TOOLS

        def executor(arguments: dict[str, Any]) -> dict[str, Any]:
            return {
                "tool_name": "test_tool",
                "input": arguments,
                "data": {"value": 42},
                "presentation": "structured summary",
            }

        try:
            server.TOOLS = {
                "test_tool": (
                    {
                        "type": "function",
                        "function": {
                            "name": "test_tool",
                            "description": "Test tool.",
                            "parameters": {"type": "object"},
                        },
                    },
                    executor,
                )
            }
            result = call_tool({"name": "test_tool", "arguments": {"x": 1}})
        finally:
            server.TOOLS = original_tools

        self.assertEqual(
            result["structuredContent"],
            {
                "tool_name": "test_tool",
                "input": {"x": 1},
                "data": {"value": 42},
                "presentation": "structured summary",
                "diagnostics": [],
            },
        )
        self.assertEqual(result["content"][0]["text"], "structured summary")
        self.assertIn('"value": 42', result["content"][1]["text"])

    def test_unknown_tool_returns_json_rpc_error(self) -> None:
        response = handle_message(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "missing", "arguments": {}},
            }
        )

        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("Tool desconhecida", response["error"]["message"])


if __name__ == "__main__":
    unittest.main()
