"""AI tool wrapper for Pokemon type damage relations."""

from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from mcp_server.src.infrastructure.pokeapi import TypeRelationsFetcher

TYPE_RELATIONS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_type_relations",
        "description": (
            "Busca o relacionamento de dano de um tipo Pokemon, incluindo tipos "
            "contra os quais ele e superefetivo, fraco ou sem efeito."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "type": {
                    "type": ["string", "integer"],
                    "description": "Nome ou ID do tipo. Exemplos: fire, water, ghost, 10.",
                },
            },
            "required": ["type"],
            "additionalProperties": False,
        },
    },
}

FetchTypeRelationsCallable = Callable[[str | int], dict[str, Any]]


def execute_type_relations_tool(
    arguments: dict[str, Any],
    fetcher: FetchTypeRelationsCallable | None = None,
) -> dict[str, Any]:
    """Execute the type relations tool with AI-provided arguments."""
    pokemon_type = arguments.get("type")
    if pokemon_type is None or (isinstance(pokemon_type, str) and not pokemon_type.strip()):
        raise ValueError("Informe o nome ou ID do tipo em 'type'.")

    selected_fetcher = fetcher or default_fetcher
    result = selected_fetcher(pokemon_type)
    return {
        "tool_name": TYPE_RELATIONS_TOOL["function"]["name"],
        "input": {"type": pokemon_type},
        "data": result,
        "presentation": format_type_relations_presentation(result),
    }


def default_fetcher(pokemon_type: str | int) -> dict[str, Any]:
    type_relations_fetcher = TypeRelationsFetcher()
    return type_relations_fetcher.fetch_type_relations(pokemon_type)


def format_type_relations_presentation(result: dict[str, Any]) -> str:
    """Build a concise text response suitable for an AI assistant."""
    pokemon_type = result["type"]
    offensive = result.get("offensive", {})
    defensive = result.get("defensive", {})
    return "\n".join(
        [
            f"Tipo: {pokemon_type['name']} (ID {pokemon_type.get('id', 'desconhecido')})",
            "Ofensivo:",
            f"- Superefetivo contra: {format_type_list(offensive.get('super_effective_against'))}",
            f"- Fraco contra: {format_type_list(offensive.get('weak_against'))}",
            f"- Sem efeito contra: {format_type_list(offensive.get('no_effect_against'))}",
            "Defensivo:",
            f"- Sofre superefetivo de: {format_type_list(defensive.get('weak_to'))}",
            f"- Resiste a: {format_type_list(defensive.get('resists'))}",
            f"- Imune a: {format_type_list(defensive.get('immune_to'))}",
        ]
    )


def format_type_list(types: list[str] | None) -> str:
    if not types:
        return "nenhum"
    return ", ".join(types)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute the Pokemon type relations AI tool.")
    parser.add_argument("type", help="Type name or id, such as fire or 10.")
    args = parser.parse_args()

    result = execute_type_relations_tool({"type": args.type})
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
