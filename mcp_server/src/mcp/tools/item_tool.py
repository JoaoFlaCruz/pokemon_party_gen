"""AI tool wrapper for listing general Pokemon items."""

from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from mcp_server.src.config.env import POKEAPI_MAX_WORKERS
from mcp_server.src.infrastructure.pokeapi import ItemFetcher

ITEM_TOOL = {
    "type": "function",
    "function": {
        "name": "list_items",
        "description": (
            "Lista itens Pokemon de maneira geral, sem depender de Pokemon especifico, "
            "incluindo categoria, custo, atributos e descricoes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Quantidade maxima de itens retornados.",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Deslocamento da paginacao de itens.",
                },
            },
            "additionalProperties": False,
        },
    },
}

FetchItemsCallable = Callable[[int, int], dict[str, Any]]


def execute_item_tool(
    arguments: dict[str, Any],
    fetcher: FetchItemsCallable | None = None,
) -> dict[str, Any]:
    """Execute the item listing tool with AI-provided arguments."""
    limit = arguments.get("limit", 20)
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        raise ValueError("'limit' deve ser um inteiro entre 1 e 100.")

    offset = arguments.get("offset", 0)
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("'offset' deve ser um inteiro maior ou igual a zero.")

    selected_fetcher = fetcher or default_fetcher
    result = selected_fetcher(limit, offset)
    return {
        "tool_name": ITEM_TOOL["function"]["name"],
        "input": {"limit": limit, "offset": offset},
        "data": result,
        "presentation": format_items_presentation(result),
    }


def default_fetcher(limit: int, offset: int) -> dict[str, Any]:
    item_fetcher = ItemFetcher()
    return item_fetcher.fetch_items(limit=limit, offset=offset)


def item_effect_description(details: dict[str, Any]) -> str | None:
    """Return the full item effect description, preferring English text."""
    effect_entries = details.get("effect_entries") or []
    if not effect_entries:
        return None

    for entry in effect_entries:
        if (entry.get("language") or {}).get("name") == "en" and entry.get("effect"):
            return entry["effect"]

    for entry in effect_entries:
        if entry.get("effect"):
            return entry["effect"]

    return None


def item_flavor_description(details: dict[str, Any]) -> str | None:
    """Return a compact flavor description, preferring English text."""
    flavor_entries = details.get("flavor_text_entries") or []
    if not flavor_entries:
        return None

    for entry in flavor_entries:
        if (entry.get("language") or {}).get("name") == "en" and entry.get("text"):
            return " ".join(entry["text"].split())

    for entry in flavor_entries:
        if entry.get("text"):
            return " ".join(entry["text"].split())

    return None


def format_items_presentation(result: dict[str, Any]) -> str:
    """Build a concise text response suitable for an AI assistant."""
    items = result.get("items", [])
    lines = [
        f"Itens encontrados: {len(items)}",
        f"Pagina: limit={result.get('limit')}, offset={result.get('offset')}, total={result.get('count')}",
        "Itens:",
    ]

    for item in items:
        category = item.get("category") or {}
        attributes = ", ".join(
            attribute.get("name", "")
            for attribute in item.get("attributes", [])
            if attribute.get("name")
        )
        effect = item_effect_description(item)
        flavor = item_flavor_description(item)
        lines.append(
            "- "
            f"{item.get('name')} "
            f"cost={item.get('cost')}, "
            f"category={category.get('name')}, "
            f"fling_power={item.get('fling_power')}, "
            f"attributes={attributes or 'nenhum'}, "
            f"effect={effect or flavor or 'sem descricao'}"
        )

    if not items:
        lines.append("- Nenhum item encontrado.")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute the general item AI tool.")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--max-workers", type=int, default=POKEAPI_MAX_WORKERS)
    args = parser.parse_args()

    def fetcher(limit: int, offset: int) -> dict[str, Any]:
        item_fetcher = ItemFetcher()
        return item_fetcher.fetch_items(
            limit=limit,
            offset=offset,
            max_workers=args.max_workers,
        )

    result = execute_item_tool(
        {"limit": args.limit, "offset": args.offset},
        fetcher=fetcher,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
