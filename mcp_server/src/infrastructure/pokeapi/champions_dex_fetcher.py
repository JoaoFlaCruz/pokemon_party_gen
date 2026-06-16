"""Fetch Pokemon Champions library membership from a PokeAPI-compatible API."""

from __future__ import annotations

import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from mcp_server.src.config.env import POKEAPI_BASE_URL, POKEAPI_TIMEOUT

CHAMPIONS_POKEDEX_IDENTIFIER = "champions"
CHAMPIONS_POKEDEX_FALLBACK_ID = "36"


class ChampionsDexFetcher:
    """Client for the Pokemon Champions Pokédex membership list."""

    def __init__(
        self,
        base_url: str = POKEAPI_BASE_URL,
        timeout: float = POKEAPI_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

    def fetch_champions_species(self) -> set[str]:
        """Return normalized species names included in the Champions Pokédex."""
        errors: list[Exception] = []
        for pokedex in (CHAMPIONS_POKEDEX_IDENTIFIER, CHAMPIONS_POKEDEX_FALLBACK_ID):
            try:
                payload = self._get_json(f"pokedex/{pokedex}/")
                species = champions_species_from_payload(payload)
                if not species:
                    raise RuntimeError(
                        f"Champions Pokédex '{pokedex}' returned no Pokemon entries."
                    )
                return species
            except RuntimeError as exc:
                errors.append(exc)

        details = "; ".join(str(error) for error in errors)
        raise RuntimeError(
            "Nao foi possivel carregar a Pokedex Champions da API configurada."
            f" Tentativas: {details}"
        )

    def _get_json(self, path: str) -> dict:
        url = urljoin(self.base_url, path)
        request = Request(url, headers={"Accept": "application/json"})

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"API request failed with HTTP {exc.code}: {url}") from exc
        except URLError as exc:
            raise RuntimeError(f"API request failed: {url}") from exc


def champions_species_from_payload(payload: dict) -> set[str]:
    """Extract normalized species names from a PokeAPI Pokédex payload."""
    species: set[str] = set()
    for entry in payload.get("pokemon_entries", []):
        species_ref = entry.get("pokemon_species") or {}
        name = str(species_ref.get("name") or "").strip().lower()
        if name:
            species.add(name)
    return species


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Pokemon Champions dex species.")
    parser.add_argument("--base-url", default=POKEAPI_BASE_URL)
    parser.add_argument("--timeout", type=float, default=POKEAPI_TIMEOUT)
    args = parser.parse_args()

    fetcher = ChampionsDexFetcher(base_url=args.base_url, timeout=args.timeout)
    result = sorted(fetcher.fetch_champions_species())
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
