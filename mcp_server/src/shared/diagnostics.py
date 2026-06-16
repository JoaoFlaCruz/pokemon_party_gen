"""Structured diagnostics shared by use cases and MCP tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

POKEMON_NOT_FOUND = "pokemon_not_found"
OUTSIDE_CHAMPIONS_SCOPE = "outside_champions_scope"
INCOMPLETE_DATA = "incomplete_data"
SOURCE_UNAVAILABLE = "source_unavailable"
UNSUPPORTED_VALIDATION = "unsupported_validation"
NO_ELIGIBLE_CANDIDATES = "no_eligible_candidates"
STRATEGY_SEARCH_TIMEOUT = "strategy_search_timeout"
STRATEGY_SEARCH_BUDGET_EXHAUSTED = "strategy_search_budget_exhausted"
PARTIAL_STRATEGY_EVIDENCE = "partial_strategy_evidence"
INVALID_STRATEGY_CASE = "invalid_strategy_case"
UNSUPPORTED_STRATEGY_PREDICATE = "unsupported_strategy_predicate"
INCOMPLETE_STRATEGY_CASE = "incomplete_strategy_case"


@dataclass(frozen=True)
class ToolDiagnostic:
    code: str
    message: str
    blocking: bool = False
    entity: str | None = None
    missing_fields: list[str] | None = None
    source: str | None = None
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "blocking": self.blocking,
        }
        if self.entity is not None:
            data["entity"] = self.entity
        if self.missing_fields:
            data["missing_fields"] = self.missing_fields
        if self.source is not None:
            data["source"] = self.source
        if self.details:
            data["details"] = self.details
        return data


class DiagnosticError(RuntimeError):
    """Exception carrying structured diagnostics for tool-safe reporting."""

    def __init__(self, diagnostic: ToolDiagnostic) -> None:
        super().__init__(diagnostic.message)
        self.diagnostic = diagnostic


def diagnostic(
    code: str,
    message: str,
    *,
    blocking: bool = False,
    entity: str | None = None,
    missing_fields: list[str] | None = None,
    source: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return ToolDiagnostic(
        code=code,
        message=message,
        blocking=blocking,
        entity=entity,
        missing_fields=missing_fields,
        source=source,
        details=details,
    ).to_dict()


def result_envelope(
    *,
    tool_name: str,
    input_data: dict[str, Any],
    data: Any,
    presentation: str,
    diagnostics: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "tool_name": tool_name,
        "input": input_data,
        "data": data,
        "presentation": presentation,
        "diagnostics": diagnostics or [],
    }
