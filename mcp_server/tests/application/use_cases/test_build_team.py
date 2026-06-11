"""Tests for Pokemon team building orchestration."""

from __future__ import annotations

import unittest
from typing import Any

from mcp_server.src.application.use_cases.build_team import build_pokemon_team


class BuildPokemonTeamTests(unittest.TestCase):
    def test_builds_complete_team_without_user_pokemon(self) -> None:
        result = build_pokemon_team(
            pokemon_lookup=self.fake_lookup,
            candidate_ranker=self.fake_ranker,
            champions_membership_checker=self.fake_champions_membership,
        )

        self.assertTrue(result["is_complete"])
        self.assertEqual(len(result["team"]), 6)
        self.assertEqual(result["team"][0]["role"], "ace")
        self.assertEqual(result["team"][3]["role"], "ace")
        self.assertEqual(result["team"][0]["trio"], "primary")
        self.assertEqual(result["team"][3]["trio"], "complementary")
        self.assertTrue(all(member["source"] == "ai" for member in result["team"]))

    def test_preserves_user_pokemon_and_records_duplicate_and_limit(self) -> None:
        result = build_pokemon_team(
            pokemon=[
                "Pikachu",
                " pikachu ",
                "charizard",
                "venusaur",
                "blastoise",
                "gengar",
                "alakazam",
                "dragonite",
            ],
            pokemon_lookup=self.fake_lookup,
            candidate_ranker=self.fake_ranker,
            champions_membership_checker=self.fake_champions_membership,
        )

        self.assertEqual(
            [member["name"] for member in result["team"]],
            ["pikachu", "charizard", "venusaur", "blastoise", "gengar", "alakazam"],
        )
        self.assertTrue(all(member["source"] == "user" for member in result["team"]))
        self.assertTrue(all(member["locked"] for member in result["team"]))
        self.assertIn("duplicate-user-pokemon", [issue["type"] for issue in result["pending"]])
        self.assertIn("team-size-limit", [issue["type"] for issue in result["pending"]])

    def test_records_unknown_pokemon_and_completes_with_candidates(self) -> None:
        result = build_pokemon_team(
            pokemon=["missingno", "pikachu"],
            pokemon_lookup=self.fake_lookup,
            candidate_ranker=self.fake_ranker,
            champions_membership_checker=self.fake_champions_membership,
        )

        self.assertTrue(result["is_complete"])
        self.assertEqual(result["team"][0]["name"], "pikachu")
        self.assertIn("unresolved-pokemon", [issue["type"] for issue in result["pending"]])
        self.assertNotIn("missingno", [member["name"] for member in result["team"]])

    def test_records_data_failure_and_insufficient_candidates(self) -> None:
        def broken_ranker(head_size: int) -> list[dict[str, Any]]:
            raise RuntimeError("api offline")

        result = build_pokemon_team(
            pokemon=["pikachu"],
            pokemon_lookup=self.fake_lookup,
            candidate_ranker=broken_ranker,
            champions_membership_checker=self.fake_champions_membership,
        )

        self.assertFalse(result["is_complete"])
        self.assertEqual([member["name"] for member in result["team"]], ["pikachu"])
        self.assertIn("candidate-data-unavailable", [issue["type"] for issue in result["pending"]])
        self.assertIn("insufficient-candidates", [issue["type"] for issue in result["pending"]])

    def test_places_two_user_aces_in_separate_trios(self) -> None:
        result = build_pokemon_team(
            pokemon=["pikachu", "charizard"],
            aces=["charizard", "pikachu"],
            primary_strategy="speed pressure",
            complementary_strategy="wallbreak",
            pokemon_lookup=self.fake_lookup,
            candidate_ranker=self.fake_ranker,
            champions_membership_checker=self.fake_champions_membership,
        )

        self.assertEqual(result["team"][0]["name"], "charizard")
        self.assertEqual(result["team"][0]["role"], "ace")
        self.assertEqual(result["team"][0]["trio"], "primary")
        self.assertEqual(result["team"][3]["name"], "pikachu")
        self.assertEqual(result["team"][3]["role"], "ace")
        self.assertEqual(result["team"][3]["trio"], "complementary")
        self.assertEqual(result["team_structure"]["primary_trio_strategy"], "speed pressure")
        self.assertEqual(result["team_structure"]["complementary_trio_strategy"], "wallbreak")
        ai_members = [member for member in result["team"] if member["source"] == "ai"]
        self.assertTrue(all(member.get("replaces_gap") for member in ai_members))


    def test_preserves_user_pokemon_outside_champions_with_pending_issue(self) -> None:
        result = build_pokemon_team(
            pokemon=["missing-from-champions"],
            pokemon_lookup=self.fake_lookup,
            candidate_ranker=self.fake_ranker,
            champions_membership_checker=self.fake_champions_membership,
        )

        self.assertEqual(result["team"][0]["name"], "missing-from-champions")
        self.assertTrue(result["team"][0]["locked"])
        self.assertFalse(result["team"][0]["champions_dex"])
        self.assertIn(
            "user-pokemon-outside-champions-dex",
            [issue["type"] for issue in result["pending"]],
        )

    def test_ai_candidates_are_marked_as_champions_members(self) -> None:
        result = build_pokemon_team(
            pokemon=["pikachu"],
            pokemon_lookup=self.fake_lookup,
            candidate_ranker=self.fake_ranker,
            champions_membership_checker=self.fake_champions_membership,
        )

        ai_members = [member for member in result["team"] if member["source"] == "ai"]
        self.assertTrue(ai_members)
        self.assertTrue(all(member["champions_dex"] for member in ai_members))
        self.assertEqual(result["selection_scope"]["ai_candidates"], "pokemon-champions")

    @staticmethod
    def fake_lookup(pokemon: str | int) -> dict[str, Any]:
        name = str(pokemon).strip().lower()
        if name == "missingno":
            raise RuntimeError("not found")
        return {
            "id": len(name),
            "name": name,
            "species": {"name": name},
            "stats": stats_for(name),
        }

    @staticmethod
    def fake_ranker(head_size: int) -> list[dict[str, Any]]:
        names = [
            "pikachu",
            "charizard",
            "venusaur",
            "blastoise",
            "gengar",
            "alakazam",
            "dragonite",
            "snorlax",
        ]
        return [
            {
                "id": index,
                "name": name,
                "stats": stats_for(name),
                "score": 500 - index,
                "champions_dex": True,
            }
            for index, name in enumerate(names[:head_size], start=1)
        ]

    @staticmethod
    def fake_champions_membership(details: dict[str, Any]) -> bool | None:
        return str(details.get("name", "")).strip().lower() != "missing-from-champions"


def stats_for(name: str) -> dict[str, int]:
    stats = {
        "hp": 80,
        "attack": 90,
        "defense": 80,
        "special-attack": 85,
        "special-defense": 80,
        "speed": 75,
    }
    if name in {"pikachu", "alakazam", "gengar"}:
        stats["speed"] = 110
        stats["special-attack"] = 120
    if name in {"charizard", "dragonite"}:
        stats["attack"] = 120
    if name in {"blastoise", "snorlax"}:
        stats["defense"] = 110
    return stats


if __name__ == "__main__":
    unittest.main()
