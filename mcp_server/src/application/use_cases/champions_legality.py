"""Validate Pokemon Champions legality and data completeness."""

from __future__ import annotations

from typing import Any, Protocol

from mcp_server.src.shared.diagnostics import (
    INCOMPLETE_DATA,
    OUTSIDE_CHAMPIONS_SCOPE,
    POKEMON_NOT_FOUND,
    SOURCE_UNAVAILABLE,
    UNSUPPORTED_VALIDATION,
    diagnostic,
)

ENTITY_POKEMON = "pokemon"
ENTITY_MOVE = "move"
ENTITY_ABILITY = "ability"
ENTITY_ITEM = "item"
ENTITY_CHOICES = (ENTITY_POKEMON, ENTITY_MOVE, ENTITY_ABILITY, ENTITY_ITEM)


class FetchesPokemonDetail(Protocol):
    def fetch_pokemon_detail(
        self,
        pokemon: str | int,
        champions_only: bool = False,
        allowed_species: set[str] | None = None,
    ) -> dict[str, Any]:
        ...


class FetchesPokemonMoves(Protocol):
    def fetch_pokemon_moves(self, pokemon: str | int, max_workers: int = 12) -> dict[str, Any]:
        ...


class FetchesItem(Protocol):
    def fetch_item(self, item: str | int) -> dict[str, Any]:
        ...


def validate_champions_legality(
    entity_type: str,
    entity: str | int,
    *,
    pokemon: str | int | None = None,
    pokemon_fetcher: FetchesPokemonDetail,
    moves_fetcher: FetchesPokemonMoves | None = None,
    item_fetcher: FetchesItem | None = None,
) -> dict[str, Any]:
    """Validate one entity against the available Pokemon Champions data."""
    normalized_type = entity_type.strip().lower()
    if normalized_type not in ENTITY_CHOICES:
        raise ValueError(
            "entity_type deve ser pokemon, move, ability ou item."
        )

    if normalized_type == ENTITY_ITEM:
        if item_fetcher is None:
            raise ValueError("item_fetcher e obrigatorio para validar item.")
        return validate_item(entity, item_fetcher)

    target_pokemon = entity if normalized_type == ENTITY_POKEMON else pokemon
    if target_pokemon is None:
        raise ValueError("'pokemon' e obrigatorio para validar move ou ability.")

    detail = fetch_detail_safely(target_pokemon, pokemon_fetcher)
    result = base_result(normalized_type, entity, detail)
    if result["diagnostics"]:
        return result

    if normalized_type == ENTITY_POKEMON:
        return result
    if normalized_type == ENTITY_ABILITY:
        return validate_ability(entity, detail, result)
    if moves_fetcher is None:
        raise ValueError("moves_fetcher e obrigatorio para validar move.")
    return validate_move(entity, target_pokemon, detail, result, moves_fetcher)


def fetch_detail_safely(
    pokemon: str | int,
    pokemon_fetcher: FetchesPokemonDetail,
) -> dict[str, Any]:
    try:
        return pokemon_fetcher.fetch_pokemon_detail(pokemon, champions_only=True)
    except RuntimeError as exc:
        return {
            "name": str(pokemon),
            "complete": False,
            "eligible": False,
            "diagnostics": [
                diagnostic(
                    POKEMON_NOT_FOUND if "HTTP 404" in str(exc) else SOURCE_UNAVAILABLE,
                    str(exc),
                    blocking=True,
                    entity=str(pokemon),
                )
            ],
        }


def base_result(entity_type: str, entity: str | int, detail: dict[str, Any]) -> dict[str, Any]:
    diagnostics = list(detail.get("diagnostics", []))
    if detail.get("champions_dex") is False:
        diagnostics.append(
            diagnostic(
                OUTSIDE_CHAMPIONS_SCOPE,
                f"Pokemon '{detail.get('name')}' esta fora do escopo Champions.",
                blocking=True,
                entity=str(detail.get("name") or entity),
            )
        )
    if detail.get("missing_fields"):
        diagnostics.append(
            diagnostic(
                INCOMPLETE_DATA,
                f"Pokemon '{detail.get('name')}' possui dados incompletos.",
                blocking=True,
                entity=str(detail.get("name") or entity),
                missing_fields=list(detail.get("missing_fields", [])),
            )
        )

    eligible = not any(item.get("blocking") for item in diagnostics) and bool(
        detail.get("eligible")
    )
    return {
        "entity_type": entity_type,
        "entity": entity,
        "checked_scope": "pokemon_champions",
        "legal": eligible,
        "eligible": eligible,
        "facts": {"pokemon": detail},
        "diagnostics": diagnostics,
        "blocking": any(item.get("blocking") for item in diagnostics),
    }


def validate_ability(entity: str | int, detail: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    ability_name = str(entity).strip().lower()
    abilities = [item.get("name") for item in detail.get("abilities", [])]
    matched = ability_name in abilities
    result["facts"]["ability"] = {"name": ability_name, "known_for_pokemon": matched}
    if not matched:
        result["legal"] = False
        result["eligible"] = False
        result["blocking"] = True
        result["diagnostics"].append(
            diagnostic(
                INCOMPLETE_DATA,
                f"Ability '{ability_name}' nao foi encontrada nos dados do Pokemon.",
                blocking=True,
                entity=ability_name,
                missing_fields=["abilities"],
            )
        )
    return result


def validate_move(
    entity: str | int,
    pokemon: str | int,
    detail: dict[str, Any],
    result: dict[str, Any],
    moves_fetcher: FetchesPokemonMoves,
) -> dict[str, Any]:
    move_name = str(entity).strip().lower()
    try:
        moves_data = moves_fetcher.fetch_pokemon_moves(pokemon)
    except RuntimeError as exc:
        result["legal"] = False
        result["eligible"] = False
        result["blocking"] = True
        result["diagnostics"].append(
            diagnostic(
                SOURCE_UNAVAILABLE,
                str(exc),
                blocking=True,
                entity=str(pokemon),
            )
        )
        return result

    known_moves = [
        (move.get("move") or {}).get("name")
        for move in moves_data.get("moves", [])
    ]
    matched = move_name in known_moves
    result["facts"]["move"] = {"name": move_name, "learned_by_pokemon": matched}
    if not matched:
        result["legal"] = False
        result["eligible"] = False
        result["blocking"] = True
        result["diagnostics"].append(
            diagnostic(
                INCOMPLETE_DATA,
                f"Move '{move_name}' nao foi encontrado no learnset validado.",
                blocking=True,
                entity=move_name,
                missing_fields=["moves"],
            )
        )
    return result


def validate_item(entity: str | int, item_fetcher: FetchesItem) -> dict[str, Any]:
    diagnostics = []
    try:
        item = item_fetcher.fetch_item(entity)
    except RuntimeError as exc:
        return {
            "entity_type": ENTITY_ITEM,
            "entity": entity,
            "checked_scope": "pokemon_champions",
            "legal": False,
            "eligible": False,
            "facts": {},
            "diagnostics": [
                diagnostic(
                    SOURCE_UNAVAILABLE,
                    str(exc),
                    blocking=True,
                    entity=str(entity),
                )
            ],
            "blocking": True,
        }

    if not item.get("name"):
        diagnostics.append(
            diagnostic(
                INCOMPLETE_DATA,
                "Item retornado sem identidade validavel.",
                blocking=True,
                entity=str(entity),
                missing_fields=["name"],
            )
        )
    diagnostics.append(
        diagnostic(
            UNSUPPORTED_VALIDATION,
            "Legalidade Champions especifica para item nao esta disponivel na fonte configurada.",
            blocking=False,
            entity=str(item.get("name") or entity),
            details={"dimension": "champions_item_legality"},
        )
    )
    return {
        "entity_type": ENTITY_ITEM,
        "entity": entity,
        "checked_scope": "pokemon_champions",
        "legal": False,
        "eligible": not any(item.get("blocking") for item in diagnostics),
        "facts": {"item": item},
        "diagnostics": diagnostics,
        "blocking": any(item.get("blocking") for item in diagnostics),
    }
