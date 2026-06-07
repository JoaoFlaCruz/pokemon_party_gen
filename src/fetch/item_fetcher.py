"""Fetch general item details from a PokeAPI-compatible REST API."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

from src.config import POKEAPI_BASE_URL, POKEAPI_MAX_WORKERS, POKEAPI_TIMEOUT


@dataclass(frozen=True)
class ItemsSummary:
    """Item list response enriched with item details."""

    count: int | None
    next: str | None
    previous: str | None
    limit: int
    offset: int
    items: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "next": self.next,
            "previous": self.previous,
            "limit": self.limit,
            "offset": self.offset,
            "items": self.items,
        }


class ItemFetcher:
    """Client for listing general items and their descriptions."""

    DETAIL_FIELDS = (
        "id",
        "name",
        "cost",
        "fling_power",
        "fling_effect",
        "attributes",
        "category",
        "effect_entries",
        "flavor_text_entries",
        "sprites",
    )

    def __init__(
        self,
        base_url: str = POKEAPI_BASE_URL,
        timeout: float = POKEAPI_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

    def fetch_items(
        self,
        limit: int = 20,
        offset: int = 0,
        max_workers: int = POKEAPI_MAX_WORKERS,
    ) -> dict[str, Any]:
        """Return a paginated item list enriched with item detail data."""
        payload = self._get_json(f"item/?limit={limit}&offset={offset}")
        item_refs = payload.get("results", [])

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            items = list(executor.map(self._fetch_item_detail_ref, item_refs))

        return ItemsSummary(
            count=payload.get("count"),
            next=payload.get("next"),
            previous=payload.get("previous"),
            limit=limit,
            offset=offset,
            items=items,
        ).to_dict()

    def _fetch_item_detail_ref(self, item_ref: dict[str, Any]) -> dict[str, Any]:
        return self.fetch_item(item_ref["name"])

    def fetch_item(self, item: str | int) -> dict[str, Any]:
        """Return one item enriched with the fields used by AI tools."""
        payload = self._get_json(f"item/{quote(str(item).strip().lower())}/")
        return {
            field: payload.get(field)
            for field in self.DETAIL_FIELDS
        }

    def _get_json(self, path: str) -> dict[str, Any]:
        url = urljoin(self.base_url, path)
        request = Request(url, headers={"Accept": "application/json"})

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"API request failed with HTTP {exc.code}: {url}") from exc
        except URLError as exc:
            raise RuntimeError(f"API request failed: {url}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch general Pokemon item details and descriptions."
    )
    parser.add_argument("--base-url", default=POKEAPI_BASE_URL)
    parser.add_argument("--timeout", type=float, default=POKEAPI_TIMEOUT)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--max-workers", type=int, default=POKEAPI_MAX_WORKERS)
    args = parser.parse_args()

    fetcher = ItemFetcher(base_url=args.base_url, timeout=args.timeout)
    result = fetcher.fetch_items(
        limit=args.limit,
        offset=args.offset,
        max_workers=args.max_workers,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
