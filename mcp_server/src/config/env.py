"""Project configuration loaded from the root .env file."""

from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"


def load_env(env_file: Path = ENV_FILE) -> None:
    """Load simple KEY=VALUE pairs into os.environ when they are not set."""
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    return float(value)


def get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


load_env()

POKEAPI_BASE_URL = os.getenv("POKEAPI_BASE_URL", "http://127.0.0.1:8000/api/v2/")
POKEAPI_TIMEOUT = get_float("POKEAPI_TIMEOUT", 30.0)
POKEAPI_MAX_WORKERS = get_int("POKEAPI_MAX_WORKERS", 12)
BANNED_POKEMON_DB_PATH = os.getenv(
    "BANNED_POKEMON_DB_PATH",
    str(ROOT_DIR / "banned_pokemon.sqlite3"),
)
