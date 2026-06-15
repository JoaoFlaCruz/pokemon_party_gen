"""AI tool wrapper for ranking one Pokemon moveset."""

from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from mcp_server.src.config.env import POKEAPI_MAX_WORKERS
from mcp_server.src.application.use_cases.rank_moveset import rank_pokemon_moveset

POKEMON_MOVESET_TOOL = {
    "type": "function",
    "function": {
        "name": "rank_pokemon_moveset",
        "description": (
            "Busca um Pokemon por nome ou ID, ranqueia seus golpes com base no "
            "melhor atributo ofensivo e retorna dados estruturados com um resumo."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "pokemon": {
                    "type": ["string", "integer"],
                    "description": "Nome ou ID do Pokemon. Exemplos: bulbasaur, pikachu, 1, 25.",
                },
                "max_moves": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Quantidade maxima de golpes ranqueados destacados no resumo.",
                },
            },
            "required": ["pokemon"],
            "additionalProperties": False,
        },
    },
}

RankMovesetCallable = Callable[[str | int], dict[str, Any]]


def execute_pokemon_moveset_tool(
    arguments: dict[str, Any],
    ranker: RankMovesetCallable | None = None,
) -> dict[str, Any]:
    """Execute the Pokemon moveset tool with AI-provided arguments."""
    pokemon = arguments.get("pokemon")
    if pokemon is None or (isinstance(pokemon, str) and not pokemon.strip()):
        raise ValueError("Informe o nome ou ID do Pokemon em 'pokemon'.")

    max_moves = arguments.get("max_moves", 10)
    if not isinstance(max_moves, int) or max_moves < 1:
        raise ValueError("'max_moves' deve ser um inteiro maior que zero.")

    selected_ranker = ranker or rank_pokemon_moveset
    result = selected_ranker(pokemon)
    return {
        "tool_name": POKEMON_MOVESET_TOOL["function"]["name"],
        "input": {"pokemon": pokemon, "max_moves": max_moves},
        "data": result,
        "presentation": format_moveset_presentation(result, max_moves=max_moves),
    }


def format_moveset_presentation(result: dict[str, Any], max_moves: int = 10) -> str:
    """Build a concise text response suitable for an AI assistant."""
    pokemon = result["pokemon"]
    stats = pokemon.get("stats", {})
    ranked_moves = [
        move for move in result.get("moves", []) if move.get("category") == "ranked"
    ]
    status_moves = [
        move for move in result.get("moves", []) if move.get("category") == "status"
    ]
    lines = [
        f"Pokemon: {pokemon['name']} (ID {pokemon.get('id', 'desconhecido')})",
        (
            "Foco ofensivo: "
            f"{result['selected_offense_stat']} "
            f"({result['selected_damage_class']})"
        ),
        f"Stats: attack={stats.get('attack')}, special-attack={stats.get('special-attack')}",
        f"Regra de ranking: {result['ranking_rule']}",
        "Melhores golpes:",
    ]

    for move in ranked_moves[:max_moves]:
        lines.append(
            "- "
            f"#{move['rank']} {move['name']} "
            f"score={move['score']:.1f}, "
            f"accuracy={move['accuracy']}, "
            f"power={move['power']}, "
            f"type={move['type']}, "
            f"class={move['damage_class']}"
        )

    if not ranked_moves:
        lines.append(
            "- Nenhum golpe ofensivo compativel com o melhor atributo foi encontrado."
        )

    if status_moves:
        lines.append(f"Golpes de status listados ao fim: {len(status_moves)}.")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute the Pokemon moveset AI tool.")
    parser.add_argument("pokemon", help="Pokemon name or id, such as bulbasaur or 1.")
    parser.add_argument("--max-moves", type=int, default=10)
    parser.add_argument("--max-workers", type=int, default=POKEAPI_MAX_WORKERS)
    args = parser.parse_args()

    def ranker(pokemon: str | int) -> dict[str, Any]:
        return rank_pokemon_moveset(pokemon, max_workers=args.max_workers)

    result = execute_pokemon_moveset_tool(
        {"pokemon": args.pokemon, "max_moves": args.max_moves},
        ranker=ranker,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
