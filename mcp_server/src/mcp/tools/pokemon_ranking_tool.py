"""AI tool wrapper for ranking Pokemon."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any, Callable

from mcp_server.src.config.env import BANNED_POKEMON_DB_PATH, POKEAPI_MAX_WORKERS
from mcp_server.src.infrastructure.pokeapi import PokemonFetcher
from mcp_server.src.application.use_cases.rank_pokemon import (
    OFFENSE_AUTO,
    OFFENSE_CHOICES,
    PRIORITY_STAT_CHOICES,
    SPEED_IGNORE,
    SPEED_MODE_CHOICES,
    rank_pokemon,
)

POKEMON_RANKING_TOOL = {
    "type": "function",
    "function": {
        "name": "rank_pokemon",
        "description": (
            "Busca Pokemon por filtros opcionais de tipo, ranqueia por stats "
            "defensivos mais um atributo ofensivo, com prioridade opcional "
            "por stat e controle de velocidade, e retorna os melhores resultados."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 2,
                    "description": (
                        "Lista opcional com ate dois tipos. Exemplos: ['fire'] "
                        "ou ['water', 'flying']."
                    ),
                },
                "offense_stat": {
                    "type": "string",
                    "enum": list(OFFENSE_CHOICES),
                    "description": (
                        "Atributo ofensivo usado na pontuacao: auto, attack "
                        "ou special-attack."
                    ),
                },
                "priority_stat": {
                    "type": "string",
                    "enum": list(PRIORITY_STAT_CHOICES),
                    "description": (
                        "Atributo que recebe multiplicador 1.4 na pontuacao: "
                        "hp, attack, defense, special-attack, special-defense ou speed."
                    ),
                },
                "speed_mode": {
                    "type": "string",
                    "enum": list(SPEED_MODE_CHOICES),
                    "description": (
                        "Controle de velocidade no ranking: ignore ignora speed, "
                        "high prioriza Pokemon rapidos e low prioriza Pokemon lentos."
                    ),
                },
                "head_size": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Quantidade maxima de Pokemon retornados no ranking.",
                },
            },
            "additionalProperties": False,
        },
    },
}

RankPokemonCallable = Callable[
    [list[str] | None, str, str | None, str, int],
    list[dict[str, Any]],
]


def execute_pokemon_ranking_tool(
    arguments: dict[str, Any],
    ranker: RankPokemonCallable | None = None,
    banned_db_path: str | Path | None = BANNED_POKEMON_DB_PATH,
) -> dict[str, Any]:
    """Execute the Pokemon ranking tool with AI-provided arguments."""
    types = validate_types(arguments.get("types"))
    offense_stat = arguments.get("offense_stat", OFFENSE_AUTO)
    if offense_stat not in OFFENSE_CHOICES:
        raise ValueError("offense_stat deve ser auto, attack ou special-attack.")

    priority_stat = arguments.get("priority_stat")
    if isinstance(priority_stat, str):
        priority_stat = priority_stat.strip().lower() or None
    if priority_stat is not None and priority_stat not in PRIORITY_STAT_CHOICES:
        raise ValueError(
            "priority_stat deve ser hp, attack, defense, special-attack, "
            "special-defense ou speed."
        )

    speed_mode = arguments.get("speed_mode", SPEED_IGNORE)
    if isinstance(speed_mode, str):
        speed_mode = speed_mode.strip().lower()
    if speed_mode not in SPEED_MODE_CHOICES:
        raise ValueError("speed_mode deve ser ignore, high ou low.")

    head_size = arguments.get("head_size", 10)
    if not isinstance(head_size, int) or head_size < 1:
        raise ValueError("'head_size' deve ser um inteiro maior que zero.")

    selected_ranker = ranker or default_ranker
    result = selected_ranker(types, offense_stat, priority_stat, speed_mode, head_size)
    result = filter_banned_pokemon(result, banned_db_path)
    return {
        "tool_name": POKEMON_RANKING_TOOL["function"]["name"],
        "input": {
            "types": types,
            "offense_stat": offense_stat,
            "priority_stat": priority_stat,
            "speed_mode": speed_mode,
            "head_size": head_size,
        },
        "data": result,
        "presentation": format_pokemon_ranking_presentation(
            result,
            types=types,
            offense_stat=offense_stat,
            priority_stat=priority_stat,
            speed_mode=speed_mode,
        ),
    }


def load_banned_pokemon(db_path: str | Path | None) -> tuple[set[int], set[str]]:
    """Load banned Pokemon identifiers from a simple SQLite database."""
    if db_path is None:
        return set(), set()

    path = Path(db_path)
    if not path.exists():
        return set(), set()

    try:
        connection = sqlite3.connect(path)
        try:
            rows = connection.execute("SELECT id, name FROM banned_pokemon").fetchall()
        finally:
            connection.close()
    except sqlite3.Error as exc:
        raise RuntimeError(
            "Nao foi possivel ler a tabela banned_pokemon do banco de Pokemon proibidos."
        ) from exc

    banned_ids = {int(row[0]) for row in rows if row[0] is not None}
    banned_names = {str(row[1]).strip().lower() for row in rows if row[1]}
    return banned_ids, banned_names


def filter_banned_pokemon(
    result: list[dict[str, Any]],
    db_path: str | Path | None,
) -> list[dict[str, Any]]:
    """Remove Pokemon present in the banned Pokemon database."""
    banned_ids, banned_names = load_banned_pokemon(db_path)
    if not banned_ids and not banned_names:
        return result

    filtered = []
    for pokemon in result:
        pokemon_id = pokemon.get("id")
        pokemon_name = str(pokemon.get("name", "")).strip().lower()
        if pokemon_id in banned_ids or pokemon_name in banned_names:
            continue
        filtered.append(pokemon)
    return filtered


def validate_types(value: Any) -> list[str] | None:
    """Validate optional Pokemon type filters for tool input."""
    if value is None:
        return None
    if not isinstance(value, list):
        raise ValueError("'types' deve ser uma lista com ate dois tipos.")

    types = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError("'types' deve conter apenas strings.")
        normalized = item.strip().lower()
        if normalized and normalized not in {"null", "none"}:
            types.append(normalized)

    if len(types) > 2:
        raise ValueError("Use no maximo dois tipos por consulta.")

    return types or None


def default_ranker(
    types: list[str] | None,
    offense_stat: str,
    priority_stat: str | None,
    speed_mode: str,
    head_size: int,
) -> list[dict[str, Any]]:
    fetcher = PokemonFetcher()
    return rank_pokemon(
        fetcher=fetcher,
        types=types,
        offense_stat=offense_stat,
        priority_stat=priority_stat,
        speed_mode=speed_mode,
        head_size=head_size,
    )


def format_pokemon_ranking_presentation(
    result: list[dict[str, Any]],
    types: list[str] | None,
    offense_stat: str,
    priority_stat: str | None,
    speed_mode: str,
) -> str:
    """Build a concise text response suitable for an AI assistant."""
    filters = ", ".join(types) if types else "todos"
    lines = [
        f"Filtro de tipos: {filters}",
        f"Atributo ofensivo solicitado: {offense_stat}",
        f"Atributo priorizado: {priority_stat or 'nenhum'}",
        f"Modo de velocidade: {speed_mode}",
        "Melhores Pokemon:",
    ]

    for index, pokemon in enumerate(result, start=1):
        parts = pokemon.get("score_parts", {})
        mega_details = ""
        if pokemon.get("is_mega"):
            required_item = pokemon.get("required_item") or {}
            mega_details = (
                f", mega_base={pokemon.get('base_pokemon')}, "
                f"mega_item={required_item.get('name') or 'desconhecido'}"
            )
        lines.append(
            "- "
            f"#{index} {pokemon['name']} "
            f"score={pokemon['score']}, "
            f"ofensa={pokemon['selected_offense_stat']}, "
            f"hp={parts.get('hp')}, "
            f"defense={parts.get('defense')}, "
            f"special-defense={parts.get('special-defense')}, "
            f"speed={parts.get('speed', 'ignorado')}"
            f"{mega_details}"
        )

    if not result:
        lines.append("- Nenhum Pokemon encontrado para os filtros informados.")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute the Pokemon ranking AI tool.")
    parser.add_argument("--type", dest="types", action="append", default=None)
    parser.add_argument("--offense-stat", choices=OFFENSE_CHOICES, default=OFFENSE_AUTO)
    parser.add_argument("--priority-stat", choices=PRIORITY_STAT_CHOICES, default=None)
    parser.add_argument("--speed-mode", choices=SPEED_MODE_CHOICES, default=SPEED_IGNORE)
    parser.add_argument("--head-size", type=int, default=10)
    parser.add_argument("--max-workers", type=int, default=POKEAPI_MAX_WORKERS)
    parser.add_argument("--banned-db-path", default=BANNED_POKEMON_DB_PATH)
    args = parser.parse_args()

    def ranker(
        types: list[str] | None,
        offense_stat: str,
        priority_stat: str | None,
        speed_mode: str,
        head_size: int,
    ) -> list[dict[str, Any]]:
        fetcher = PokemonFetcher()
        return rank_pokemon(
            fetcher=fetcher,
            types=types,
            offense_stat=offense_stat,
            priority_stat=priority_stat,
            speed_mode=speed_mode,
            head_size=head_size,
            max_workers=args.max_workers,
        )

    result = execute_pokemon_ranking_tool(
        {
            "types": args.types,
            "offense_stat": args.offense_stat,
            "priority_stat": args.priority_stat,
            "speed_mode": args.speed_mode,
            "head_size": args.head_size,
        },
        ranker=ranker,
        banned_db_path=args.banned_db_path,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
