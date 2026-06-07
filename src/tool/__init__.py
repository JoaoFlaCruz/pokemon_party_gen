"""AI tool helpers."""

from __future__ import annotations

from typing import Any

__all__ = [
    "BAN_POKEMON_TOOL",
    "ITEM_TOOL",
    "POKEMON_MOVESET_TOOL",
    "POKEMON_RANKING_TOOL",
    "TYPE_RELATIONS_TOOL",
    "execute_ban_pokemon_tool",
    "execute_item_tool",
    "execute_pokemon_moveset_tool",
    "execute_pokemon_ranking_tool",
    "execute_type_relations_tool",
]


def __getattr__(name: str) -> Any:
    if name in {"BAN_POKEMON_TOOL", "execute_ban_pokemon_tool"}:
        from . import banned_pokemon_tool

        return getattr(banned_pokemon_tool, name)
    if name in {"ITEM_TOOL", "execute_item_tool"}:
        from . import item_tool

        return getattr(item_tool, name)
    if name in {"TYPE_RELATIONS_TOOL", "execute_type_relations_tool"}:
        from . import type_relations_tool

        return getattr(type_relations_tool, name)
    if name in {"POKEMON_MOVESET_TOOL", "execute_pokemon_moveset_tool"}:
        from . import pokemon_moveset_tool

        return getattr(pokemon_moveset_tool, name)
    if name in {"POKEMON_RANKING_TOOL", "execute_pokemon_ranking_tool"}:
        from . import pokemon_ranking_tool

        return getattr(pokemon_ranking_tool, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
