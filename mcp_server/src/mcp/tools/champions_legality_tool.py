"""MCP tool for Pokemon Champions legality validation."""

from __future__ import annotations

import json
from typing import Any, Callable

from mcp_server.src.application.use_cases.champions_legality import (
    ENTITY_CHOICES,
    validate_champions_legality,
)
from mcp_server.src.infrastructure.pokeapi import ItemFetcher, PokemonFetcher, PokemonMovesFetcher
from mcp_server.src.shared.diagnostics import result_envelope

CHAMPIONS_LEGALITY_TOOL = {
    "type": "function",
    "function": {
        "name": "validate_champions_legality",
        "description": (
            "Valida Pokemon, golpe, habilidade ou item contra dados Pokemon Champions "
            "e retorna fatos, elegibilidade e diagnosticos estruturados."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "entity_type": {
                    "type": "string",
                    "enum": list(ENTITY_CHOICES),
                    "description": "Tipo de entidade: pokemon, move, ability ou item.",
                },
                "entity": {
                    "type": ["string", "integer"],
                    "description": "Nome ou ID da entidade a validar.",
                },
                "pokemon": {
                    "type": ["string", "integer"],
                    "description": "Pokemon relacionado quando entity_type for move ou ability.",
                },
            },
            "required": ["entity_type", "entity"],
            "additionalProperties": False,
        },
    },
}

LegalityCallable = Callable[[str, str | int, str | int | None], dict[str, Any]]


def execute_champions_legality_tool(
    arguments: dict[str, Any],
    validator: LegalityCallable | None = None,
) -> dict[str, Any]:
    entity_type = arguments.get("entity_type")
    entity = arguments.get("entity")
    pokemon = arguments.get("pokemon")
    if not isinstance(entity_type, str) or not entity_type.strip():
        raise ValueError("Informe entity_type.")
    if entity is None or (isinstance(entity, str) and not entity.strip()):
        raise ValueError("Informe entity.")

    selected_validator = validator or default_validator
    data = selected_validator(entity_type, entity, pokemon)
    return result_envelope(
        tool_name=CHAMPIONS_LEGALITY_TOOL["function"]["name"],
        input_data={"entity_type": entity_type, "entity": entity, "pokemon": pokemon},
        data=data,
        presentation=format_legality_presentation(data),
        diagnostics=data.get("diagnostics", []),
    )


def default_validator(
    entity_type: str,
    entity: str | int,
    pokemon: str | int | None,
) -> dict[str, Any]:
    return validate_champions_legality(
        entity_type,
        entity,
        pokemon=pokemon,
        pokemon_fetcher=PokemonFetcher(),
        moves_fetcher=PokemonMovesFetcher(),
        item_fetcher=ItemFetcher(),
    )


def format_legality_presentation(data: dict[str, Any]) -> str:
    lines = [
        f"Entidade: {data.get('entity_type')}={data.get('entity')}",
        f"Escopo: {data.get('checked_scope')}",
        f"Elegivel: {data.get('eligible')}",
        f"Legal: {data.get('legal')}",
    ]
    for item in data.get("diagnostics", []):
        lines.append(f"Diagnostico: {item.get('code')} - {item.get('message')}")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Validate Pokemon Champions legality.")
    parser.add_argument("entity_type", choices=ENTITY_CHOICES)
    parser.add_argument("entity")
    parser.add_argument("--pokemon")
    args = parser.parse_args()
    result = execute_champions_legality_tool(
        {"entity_type": args.entity_type, "entity": args.entity, "pokemon": args.pokemon}
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
