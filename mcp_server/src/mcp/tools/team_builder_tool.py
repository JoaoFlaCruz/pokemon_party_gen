"""AI tool wrapper for building a complete Pokemon team."""

from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from mcp_server.src.application.use_cases.build_team import build_pokemon_team

TEAM_BUILDER_TOOL = {
    "type": "function",
    "function": {
        "name": "build_pokemon_team",
        "description": (
            "Monta um time de 6 Pokemon a partir de escolhas do usuario, "
            "preservando membros fixos, separando dois trios e declarando pendencias."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "pokemon": {
                    "type": "array",
                    "items": {"type": ["string", "integer"]},
                    "description": "Pokemon escolhidos pelo usuario, por nome ou ID.",
                },
                "aces": {
                    "type": "array",
                    "items": {"type": ["string", "integer"]},
                    "maxItems": 2,
                    "description": "Ate dois Pokemon que devem liderar os trios.",
                },
                "primary_strategy": {
                    "type": "string",
                    "description": "Estrategia desejada para o trio principal.",
                },
                "complementary_strategy": {
                    "type": "string",
                    "description": "Estrategia desejada para o trio complementar.",
                },
            },
            "additionalProperties": False,
        },
    },
}

BuildTeamCallable = Callable[
    [list[str | int] | None, str | None, str | None, list[str | int] | None],
    dict[str, Any],
]


def execute_team_builder_tool(
    arguments: dict[str, Any],
    builder: BuildTeamCallable | None = None,
) -> dict[str, Any]:
    """Execute the Pokemon team builder tool with AI-provided arguments."""
    pokemon = validate_optional_identifier_list(arguments.get("pokemon"), "pokemon")
    aces = validate_optional_identifier_list(arguments.get("aces"), "aces", max_items=2)
    primary_strategy = validate_optional_text(arguments.get("primary_strategy"), "primary_strategy")
    complementary_strategy = validate_optional_text(
        arguments.get("complementary_strategy"),
        "complementary_strategy",
    )

    selected_builder = builder or default_builder
    data = selected_builder(pokemon, primary_strategy, complementary_strategy, aces)
    return {
        "tool_name": TEAM_BUILDER_TOOL["function"]["name"],
        "input": {
            "pokemon": pokemon,
            "aces": aces,
            "primary_strategy": primary_strategy,
            "complementary_strategy": complementary_strategy,
        },
        "data": data,
        "presentation": format_team_presentation(data),
    }


def default_builder(
    pokemon: list[str | int] | None,
    primary_strategy: str | None,
    complementary_strategy: str | None,
    aces: list[str | int] | None,
) -> dict[str, Any]:
    return build_pokemon_team(
        pokemon=pokemon,
        primary_strategy=primary_strategy,
        complementary_strategy=complementary_strategy,
        aces=aces,
    )


def validate_optional_identifier_list(
    value: Any,
    field_name: str,
    max_items: int | None = None,
) -> list[str | int] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ValueError(f"'{field_name}' deve ser uma lista de strings ou inteiros.")
    if max_items is not None and len(value) > max_items:
        raise ValueError(f"'{field_name}' deve conter no maximo {max_items} itens.")

    result: list[str | int] = []
    for item in value:
        if isinstance(item, int):
            if item < 1:
                raise ValueError(f"'{field_name}' deve conter IDs maiores que zero.")
            result.append(item)
        elif isinstance(item, str):
            normalized = item.strip().lower()
            if not normalized:
                raise ValueError(f"'{field_name}' nao pode conter nomes vazios.")
            result.append(normalized)
        else:
            raise ValueError(f"'{field_name}' deve conter apenas strings ou inteiros.")

    return result


def validate_optional_text(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"'{field_name}' deve ser uma string.")
    return value.strip() or None


def format_team_presentation(data: dict[str, Any]) -> str:
    """Build a concise text response suitable for an AI assistant."""
    structure = data.get("team_structure", {})
    lines = [
        f"Time Pokemon: {'completo' if data.get('is_complete') else 'parcial'}",
        f"Tamanho alvo: {data.get('team_size')}",
        f"Escopo AI: {data.get('selection_scope', {}).get('ai_candidates', 'pokemon-champions')}",
        f"Trio principal - estrategia={structure.get('primary_trio_strategy')}",
    ]

    for index, member in enumerate(data.get("team", []), start=1):
        if index == 4:
            lines.append(
                "Trio complementar - "
                f"estrategia={structure.get('complementary_trio_strategy')}"
            )
        lines.append(
            "- "
            f"{index}. {member.get('name')} "
            f"source={member.get('source')} "
            f"locked={str(member.get('locked')).lower()} "
            f"role={member.get('role')} "
            f"champions_dex={member.get('champions_dex', 'desconhecido')}"
        )
        lines.append(f"  Motivo: {member.get('reason')}")
        if member.get("replaces_gap"):
            lines.append(f"  Lacuna: {member.get('replaces_gap')}")

    pending = data.get("pending", [])
    if pending:
        lines.append("Pendencias:")
        for issue in pending:
            lines.append(f"- {issue.get('type')}: {issue.get('reason')}")
    else:
        lines.append("Pendencias: nenhuma")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute the Pokemon team builder AI tool.")
    parser.add_argument("--pokemon", action="append", default=None)
    parser.add_argument("--ace", dest="aces", action="append", default=None)
    parser.add_argument("--primary-strategy", default=None)
    parser.add_argument("--complementary-strategy", default=None)
    args = parser.parse_args()

    result = execute_team_builder_tool(
        {
            "pokemon": args.pokemon,
            "aces": args.aces,
            "primary_strategy": args.primary_strategy,
            "complementary_strategy": args.complementary_strategy,
        }
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
