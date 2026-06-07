"""AI tool wrapper for registering banned Pokemon."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from src.config import BANNED_POKEMON_DB_PATH

BANNED_POKEMON_TABLE = "banned_pokemon"

BAN_POKEMON_TOOL = {
    "type": "function",
    "function": {
        "name": "ban_pokemon",
        "description": (
            "Registra um Pokemon proibido no banco SQLite de exclusao, usando "
            "o ID numerico do Pokemon e seu nome."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "ID numerico do Pokemon a ser proibido.",
                },
                "name": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Nome do Pokemon a ser proibido.",
                },
            },
            "required": ["id", "name"],
            "additionalProperties": False,
        },
    },
}


def execute_ban_pokemon_tool(
    arguments: dict[str, Any],
    db_path: str | Path = BANNED_POKEMON_DB_PATH,
) -> dict[str, Any]:
    """Execute the banned Pokemon registration tool."""
    pokemon_id = validate_pokemon_id(arguments.get("id"))
    pokemon_name = validate_pokemon_name(arguments.get("name"))

    created = add_banned_pokemon(pokemon_id, pokemon_name, db_path)
    data = {
        "pokemon": {"id": pokemon_id, "name": pokemon_name},
        "created": created,
        "db_path": str(db_path),
    }
    return {
        "tool_name": BAN_POKEMON_TOOL["function"]["name"],
        "input": {"id": pokemon_id, "name": pokemon_name},
        "data": data,
        "presentation": format_ban_pokemon_presentation(data),
    }


def validate_pokemon_id(value: Any) -> int:
    if not isinstance(value, int) or value < 1:
        raise ValueError("'id' deve ser um inteiro maior que zero.")
    return value


def validate_pokemon_name(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("'name' deve ser uma string nao vazia.")
    normalized = value.strip().lower()
    if not normalized:
        raise ValueError("'name' deve ser uma string nao vazia.")
    return normalized


def add_banned_pokemon(pokemon_id: int, pokemon_name: str, db_path: str | Path) -> bool:
    """Insert a banned Pokemon in SQLite and return True when a row is created."""
    path = Path(db_path)
    if path.parent != Path(""):
        path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with sqlite3.connect(path) as connection:
            connection.execute(
                f"CREATE TABLE IF NOT EXISTS {BANNED_POKEMON_TABLE} "
                "(id INTEGER NOT NULL, name TEXT NOT NULL)"
            )
            existing = connection.execute(
                f"SELECT 1 FROM {BANNED_POKEMON_TABLE} "
                "WHERE id = ? OR lower(name) = ? LIMIT 1",
                (pokemon_id, pokemon_name),
            ).fetchone()
            if existing:
                return False
            connection.execute(
                f"INSERT INTO {BANNED_POKEMON_TABLE} (id, name) VALUES (?, ?)",
                (pokemon_id, pokemon_name),
            )
    except sqlite3.Error as exc:
        raise RuntimeError(
            "Nao foi possivel registrar o Pokemon no banco de exclusao."
        ) from exc

    return True


def format_ban_pokemon_presentation(data: dict[str, Any]) -> str:
    pokemon = data["pokemon"]
    status = "registrado" if data["created"] else "ja estava registrado"
    return (
        f"Pokemon proibido: {pokemon['name']} (ID {pokemon['id']}) - {status}.\n"
        f"Banco: {data['db_path']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Register a banned Pokemon for ranking tools.")
    parser.add_argument("id", type=int)
    parser.add_argument("name")
    parser.add_argument("--db-path", default=BANNED_POKEMON_DB_PATH)
    args = parser.parse_args()

    result = execute_ban_pokemon_tool(
        {"id": args.id, "name": args.name},
        db_path=args.db_path,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
