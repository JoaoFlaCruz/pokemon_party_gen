"""Search Pokemon Champions candidates by strategic role or injected case."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from mcp_server.src.shared.diagnostics import (
    INCOMPLETE_DATA,
    INCOMPLETE_STRATEGY_CASE,
    INVALID_STRATEGY_CASE,
    NO_ELIGIBLE_CANDIDATES,
    PARTIAL_STRATEGY_EVIDENCE,
    SOURCE_UNAVAILABLE,
    STRATEGY_SEARCH_BUDGET_EXHAUSTED,
    STRATEGY_SEARCH_TIMEOUT,
    UNSUPPORTED_STRATEGY_PREDICATE,
    diagnostic,
)

ROLE_CHOICES = (
    "rain-setter",
    "rain-attacker",
    "defensive-pivot",
    "ground-check",
    "fighting-check",
    "fire-check",
    "speed-control",
    "win-condition",
)

DEFAULT_CANDIDATE_SCAN_LIMIT = 24
DEFAULT_EVALUATION_LIMIT = 24
STAT_CHOICES = {
    "hp",
    "attack",
    "defense",
    "special-attack",
    "special-defense",
    "speed",
    "offense",
    "bulk",
}
QUERY_SOURCES = {"ability", "move", "types", "stat_profile"}
EVIDENCE_KINDS = {"ability", "move", "type", "stat_profile"}


@dataclass(frozen=True)
class StrategyQuery:
    source: str
    types: tuple[str, ...] = ()
    ability: str | None = None
    move: str | None = None
    stat: str | None = None
    min_value: int | None = None
    label: str | None = None

    def to_fetch_kwargs(self) -> dict[str, Any]:
        return {
            "types": list(self.types) if self.types else None,
            "ability": self.ability,
            "move": self.move,
            "champions_only": True,
        }

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "source": self.source,
            "types": list(self.types),
            "ability": self.ability,
            "move": self.move,
        }
        if self.stat is not None:
            data["stat"] = self.stat
        if self.min_value is not None:
            data["min"] = self.min_value
        if self.label is not None:
            data["label"] = self.label
        return data


@dataclass(frozen=True)
class StrategyCase:
    name: str
    queries: tuple[StrategyQuery, ...]
    evidence_any: tuple[dict[str, Any], ...]
    injected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "queries": [query.to_dict() for query in self.queries],
            "evidence": {"any": [dict(item) for item in self.evidence_any]},
        }


class StrategyCaseError(ValueError):
    """Raised when a caller-supplied strategy case cannot be executed."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.diagnostic = diagnostic(code, message, blocking=True, details=details)


BUILT_IN_CASES: dict[str, StrategyCase] = {
    "rain-setter": StrategyCase(
        name="rain-setter",
        queries=(
            StrategyQuery("ability", ability="drizzle"),
            StrategyQuery("move", move="rain-dance"),
        ),
        evidence_any=(
            {"kind": "ability", "name": "drizzle"},
            {"kind": "move", "name": "rain-dance"},
        ),
    ),
    "rain-attacker": StrategyCase(
        name="rain-attacker",
        queries=(
            StrategyQuery("ability", ability="swift-swim"),
            StrategyQuery("ability", ability="rain-dish"),
            StrategyQuery("types", types=("water",)),
        ),
        evidence_any=(
            {"kind": "ability", "name": "swift-swim"},
            {"kind": "ability", "name": "rain-dish"},
            {"kind": "type", "name": "water"},
            {"kind": "stat_profile", "name": "high-offense", "stat": "offense", "min": 110},
        ),
    ),
    "defensive-pivot": StrategyCase(
        name="defensive-pivot",
        queries=(
            StrategyQuery("types", types=("steel",)),
            StrategyQuery("types", types=("water",)),
            StrategyQuery("types", types=("grass",)),
        ),
        evidence_any=(
            {"kind": "stat_profile", "name": "defensive-bulk", "stat": "bulk", "min": 270},
        ),
    ),
    "ground-check": StrategyCase(
        name="ground-check",
        queries=(
            StrategyQuery("types", types=("flying",)),
            StrategyQuery("types", types=("grass",)),
            StrategyQuery("types", types=("water",)),
        ),
        evidence_any=(
            {"kind": "type", "name": "flying"},
            {"kind": "type", "name": "grass"},
            {"kind": "type", "name": "water"},
        ),
    ),
    "fighting-check": StrategyCase(
        name="fighting-check",
        queries=(
            StrategyQuery("types", types=("flying",)),
            StrategyQuery("types", types=("fairy",)),
            StrategyQuery("types", types=("psychic",)),
            StrategyQuery("types", types=("ghost",)),
        ),
        evidence_any=(
            {"kind": "type", "name": "flying"},
            {"kind": "type", "name": "fairy"},
            {"kind": "type", "name": "psychic"},
            {"kind": "type", "name": "ghost"},
        ),
    ),
    "fire-check": StrategyCase(
        name="fire-check",
        queries=(
            StrategyQuery("types", types=("water",)),
            StrategyQuery("types", types=("dragon",)),
            StrategyQuery("types", types=("fire",)),
            StrategyQuery("types", types=("rock",)),
        ),
        evidence_any=(
            {"kind": "type", "name": "water"},
            {"kind": "type", "name": "dragon"},
            {"kind": "type", "name": "fire"},
            {"kind": "type", "name": "rock"},
        ),
    ),
    "speed-control": StrategyCase(
        name="speed-control",
        queries=(
            StrategyQuery("move", move="tailwind"),
            StrategyQuery("move", move="icy-wind"),
            StrategyQuery("move", move="thunder-wave"),
            StrategyQuery("stat_profile", stat="speed", min_value=100, label="high-speed"),
        ),
        evidence_any=(
            {"kind": "move", "name": "tailwind"},
            {"kind": "move", "name": "icy-wind"},
            {"kind": "move", "name": "thunder-wave"},
            {"kind": "stat_profile", "name": "high-speed", "stat": "speed", "min": 100},
        ),
    ),
    "win-condition": StrategyCase(
        name="win-condition",
        queries=(
            StrategyQuery("move", move="dragon-dance"),
            StrategyQuery("move", move="calm-mind"),
            StrategyQuery("move", move="swords-dance"),
            StrategyQuery("move", move="nasty-plot"),
            StrategyQuery("move", move="iron-defense"),
            StrategyQuery("stat_profile", stat="offense", min_value=120, label="high-offense"),
        ),
        evidence_any=(
            {"kind": "move", "name": "dragon-dance"},
            {"kind": "move", "name": "calm-mind"},
            {"kind": "move", "name": "swords-dance"},
            {"kind": "move", "name": "nasty-plot"},
            {"kind": "move", "name": "iron-defense"},
            {"kind": "stat_profile", "name": "high-offense", "stat": "offense", "min": 120},
        ),
    ),
}


class FetchesPokemon(Protocol):
    def fetch_pokemon(
        self,
        types: list[str] | tuple[str, ...] | None = None,
        ability: str | None = None,
        move: str | None = None,
        champions_only: bool = False,
        allowed_species: set[str] | None = None,
        max_workers: int = 12,
    ) -> list[dict[str, Any]]:
        ...


class FetchesPokemonMoves(Protocol):
    def fetch_pokemon_moves(self, pokemon: str | int, max_workers: int = 12) -> dict[str, Any]:
        ...


def search_champions_strategy(
    role: str | None = None,
    *,
    case: dict[str, Any] | None = None,
    fetcher: FetchesPokemon,
    moves_fetcher: FetchesPokemonMoves | None = None,
    head_size: int = 10,
    candidate_scan_limit: int = DEFAULT_CANDIDATE_SCAN_LIMIT,
    evaluation_limit: int = DEFAULT_EVALUATION_LIMIT,
    max_workers: int = 4,
) -> dict[str, Any]:
    if head_size < 1:
        raise ValueError("head_size deve ser maior que zero.")
    if candidate_scan_limit < 1:
        raise ValueError("candidate_scan_limit deve ser maior que zero.")
    if evaluation_limit < 1:
        raise ValueError("evaluation_limit deve ser maior que zero.")

    strategy_case, normalized_role = resolve_strategy_case(role, case)
    context_name = normalized_role or strategy_case.name
    diagnostics = []
    allowed_species = load_allowed_species_if_available(fetcher, diagnostics, context_name)
    search_plan = [query.to_dict() for query in strategy_case.queries]
    candidates, query_diagnostics = fetch_case_candidates(
        strategy_case,
        fetcher,
        candidate_scan_limit=candidate_scan_limit,
        max_workers=max_workers,
        allowed_species=allowed_species,
    )
    diagnostics.extend(query_diagnostics)
    fallback_used = False
    if not candidates:
        fallback_used = True
        search_plan.append(
            {
                "source": "fallback",
                "types": [],
                "ability": None,
                "move": None,
                "candidate_scan_limit": candidate_scan_limit,
            }
        )
        fallback_candidates, fallback_diagnostics = fetch_fallback_candidates(
            fetcher,
            context_name=context_name,
            candidate_scan_limit=candidate_scan_limit,
            max_workers=max_workers,
            allowed_species=allowed_species,
        )
        candidates = fallback_candidates
        diagnostics.extend(fallback_diagnostics)

    matched = []
    pending = []
    excluded = []
    evaluated_count = 0
    partial_results = any(item.get("code") == STRATEGY_SEARCH_BUDGET_EXHAUSTED for item in diagnostics)

    for pokemon in candidates:
        if evaluated_count >= evaluation_limit:
            partial_results = True
            diagnostics.append(
                diagnostic(
                    STRATEGY_SEARCH_BUDGET_EXHAUSTED,
                    f"Limite de avaliacao atingido para strategy case '{strategy_case.name}'.",
                    details={
                        "role": normalized_role,
                        "case_name": strategy_case.name,
                        "evaluation_limit": evaluation_limit,
                    },
                )
            )
            break
        champions_dex = pokemon.get("champions_dex")
        if champions_dex is not True:
            excluded.append(
                {
                    "pokemon": pokemon.get("name"),
                    "reason": "champions_dex_not_true",
                    "champions_dex": champions_dex,
                }
            )
            continue
        evaluated_count += 1
        evidence = case_evidence(strategy_case, pokemon, moves_fetcher)
        if evidence["matched"]:
            candidate = {
                "pokemon": pokemon,
                "evidence": evidence["evidence"],
                "champions_dex": pokemon.get("champions_dex"),
            }
            if normalized_role:
                candidate["role"] = normalized_role
            if strategy_case.injected:
                candidate["case_name"] = strategy_case.name
            matched.append(candidate)
        elif evidence["pending"]:
            pending.append({"pokemon": pokemon.get("name"), "pending": evidence["pending"]})

    matched = matched[:head_size]
    if not matched:
        diagnostics.append(
            diagnostic(
                NO_ELIGIBLE_CANDIDATES,
                f"Nenhum candidato Champions encontrado para strategy case '{strategy_case.name}'.",
                details={
                    "role": normalized_role,
                    "case_name": strategy_case.name,
                    "champions_only": True,
                    "candidate_count": len(candidates),
                    "evaluated_count": evaluated_count,
                    "excluded_count": len(excluded),
                    "partial_results": partial_results,
                    "pending": pending,
                },
            )
        )
    if pending:
        diagnostics.append(
            diagnostic(
                PARTIAL_STRATEGY_EVIDENCE,
                f"Alguns candidatos exigem dados adicionais para strategy case '{strategy_case.name}'.",
                details={"role": normalized_role, "case_name": strategy_case.name, "pending": pending},
            )
        )
    if excluded:
        diagnostics.append(
            diagnostic(
                INCOMPLETE_DATA,
                "Candidatos excluidos porque Champions membership nao foi comprovada.",
                details={"excluded": excluded},
            )
        )

    result = {
        "role": normalized_role,
        "champions_only": True,
        "candidates": matched,
        "pending": pending,
        "diagnostics": diagnostics,
        "candidate_count": len(candidates),
        "evaluated_count": evaluated_count,
        "excluded_count": len(excluded),
        "excluded": excluded,
        "partial_results": partial_results,
        "search_plan": search_plan,
        "fallback_used": fallback_used,
    }
    if strategy_case.injected:
        result["case_name"] = strategy_case.name
        result["case"] = strategy_case.to_dict()
    return result


def resolve_strategy_case(role: str | None, case: dict[str, Any] | None) -> tuple[StrategyCase, str | None]:
    has_role = isinstance(role, str) and bool(role.strip())
    has_case = case is not None
    if has_role and has_case:
        raise StrategyCaseError(
            INVALID_STRATEGY_CASE,
            "Informe role ou case, nao ambos.",
            {"role": role, "case_name": case.get("name") if isinstance(case, dict) else None},
        )
    if not has_role and not has_case:
        raise StrategyCaseError(INCOMPLETE_STRATEGY_CASE, "Informe role ou case.")
    if has_case:
        if not isinstance(case, dict):
            raise StrategyCaseError(INVALID_STRATEGY_CASE, "case deve ser um objeto JSON.")
        return normalize_strategy_case(case), None

    normalized_role = str(role).strip().lower()
    if normalized_role not in BUILT_IN_CASES:
        raise ValueError(f"role deve ser um de: {', '.join(ROLE_CHOICES)}.")
    return BUILT_IN_CASES[normalized_role], normalized_role


def normalize_strategy_case(raw_case: dict[str, Any]) -> StrategyCase:
    name = normalize_name(raw_case.get("name"))
    queries = tuple(normalize_query(item) for item in raw_case.get("queries", []))
    evidence = raw_case.get("evidence")
    if not queries:
        raise StrategyCaseError(INCOMPLETE_STRATEGY_CASE, "case precisa de ao menos uma query.")
    if not isinstance(evidence, dict):
        raise StrategyCaseError(INCOMPLETE_STRATEGY_CASE, "case precisa de evidence.")
    raw_any = evidence.get("any")
    if not isinstance(raw_any, list) or not raw_any:
        raise StrategyCaseError(INCOMPLETE_STRATEGY_CASE, "case.evidence.any precisa de ao menos uma regra.")
    evidence_any = tuple(normalize_evidence_rule(item) for item in raw_any)
    return StrategyCase(name=name, queries=queries, evidence_any=evidence_any, injected=True)


def normalize_name(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StrategyCaseError(INCOMPLETE_STRATEGY_CASE, "case.name e obrigatorio.")
    return value.strip().lower().replace("_", "-")


def normalize_query(raw_query: Any) -> StrategyQuery:
    if not isinstance(raw_query, dict):
        raise StrategyCaseError(INVALID_STRATEGY_CASE, "Cada query deve ser um objeto.")
    source = normalize_token(raw_query.get("source"))
    if source not in QUERY_SOURCES:
        raise StrategyCaseError(
            UNSUPPORTED_STRATEGY_PREDICATE,
            f"Fonte de query nao suportada: {source or raw_query.get('source')}.",
            {"query": raw_query},
        )
    if source == "ability":
        ability = normalize_required_token(raw_query.get("ability"), "query ability")
        return StrategyQuery(source, ability=ability)
    if source == "move":
        move = normalize_required_token(raw_query.get("move"), "query move")
        return StrategyQuery(source, move=move)
    if source == "types":
        types = normalize_types(raw_query)
        return StrategyQuery(source, types=types)
    stat = normalize_required_token(raw_query.get("stat"), "query stat")
    min_value = normalize_min_value(raw_query)
    label = normalize_token(raw_query.get("label")) or f"{stat}-min-{min_value}"
    validate_stat(stat, raw_query)
    return StrategyQuery(source, stat=stat, min_value=min_value, label=label)


def normalize_evidence_rule(raw_rule: Any) -> dict[str, Any]:
    if not isinstance(raw_rule, dict):
        raise StrategyCaseError(INVALID_STRATEGY_CASE, "Cada regra de evidencia deve ser um objeto.")
    kind = normalize_token(raw_rule.get("kind"))
    if kind not in EVIDENCE_KINDS:
        raise StrategyCaseError(
            UNSUPPORTED_STRATEGY_PREDICATE,
            f"Tipo de evidencia nao suportado: {kind or raw_rule.get('kind')}.",
            {"evidence": raw_rule},
        )
    if kind in {"ability", "move", "type"}:
        return {"kind": kind, "name": normalize_required_token(raw_rule.get("name"), f"{kind} evidence")}
    stat = normalize_required_token(raw_rule.get("stat"), "stat evidence")
    validate_stat(stat, raw_rule)
    min_value = normalize_min_value(raw_rule)
    label = normalize_token(raw_rule.get("name")) or normalize_token(raw_rule.get("label")) or f"{stat}-min-{min_value}"
    return {"kind": kind, "name": label, "stat": stat, "min": min_value}


def fetch_case_candidates(
    strategy_case: StrategyCase,
    fetcher: FetchesPokemon,
    *,
    candidate_scan_limit: int,
    max_workers: int,
    allowed_species: set[str] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates: dict[str, dict[str, Any]] = {}
    diagnostics = []
    for query in strategy_case.queries:
        if query.source == "stat_profile":
            continue
        try:
            fetched = fetcher.fetch_pokemon(
                **query.to_fetch_kwargs(),
                allowed_species=allowed_species,
                max_workers=max_workers,
            )
        except RuntimeError as exc:
            diagnostics.append(source_failure_diagnostic(strategy_case.name, query.to_dict(), exc))
            continue
        merge_candidates(candidates, fetched)
        if len(candidates) >= candidate_scan_limit:
            diagnostics.append(
                diagnostic(
                    STRATEGY_SEARCH_BUDGET_EXHAUSTED,
                    f"Limite de candidatos atingido para strategy case '{strategy_case.name}'.",
                    details={
                        "case_name": strategy_case.name,
                        "candidate_scan_limit": candidate_scan_limit,
                    },
                )
            )
            break
    return list(candidates.values())[:candidate_scan_limit], diagnostics


def fetch_fallback_candidates(
    fetcher: FetchesPokemon,
    *,
    context_name: str,
    candidate_scan_limit: int,
    max_workers: int,
    allowed_species: set[str] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    diagnostics = [
        diagnostic(
            STRATEGY_SEARCH_BUDGET_EXHAUSTED,
            "Fallback amplo de Champions esta limitado por orcamento de candidatos.",
            details={"case_name": context_name, "candidate_scan_limit": candidate_scan_limit},
        )
    ]
    try:
        candidates = fetcher.fetch_pokemon(
            champions_only=True,
            allowed_species=allowed_species,
            max_workers=max_workers,
        )
    except RuntimeError as exc:
        return [], [source_failure_diagnostic(context_name, {"source": "fallback"}, exc)]
    return candidates[:candidate_scan_limit], diagnostics


def load_allowed_species_if_available(
    fetcher: FetchesPokemon,
    diagnostics: list[dict[str, Any]],
    context_name: str,
) -> set[str] | None:
    loader = getattr(fetcher, "_champions_species", None)
    if not callable(loader):
        return None
    try:
        return loader(True, None)
    except RuntimeError as exc:
        diagnostics.append(
            diagnostic(
                SOURCE_UNAVAILABLE,
                str(exc),
                blocking=True,
                details={"case_name": context_name, "source": "champions_membership"},
            )
        )
        return None


def merge_candidates(target: dict[str, dict[str, Any]], candidates: list[dict[str, Any]]) -> None:
    for pokemon in candidates:
        key = normalized_pokemon_key(pokemon)
        if key and key not in target:
            target[key] = pokemon


def normalized_pokemon_key(pokemon: dict[str, Any]) -> str:
    species = pokemon.get("species")
    if isinstance(species, dict) and species.get("name"):
        return str(species["name"]).strip().lower()
    return str(pokemon.get("name", "")).strip().lower()


def source_failure_diagnostic(context_name: str, query: dict[str, Any], exc: RuntimeError) -> dict[str, Any]:
    message = str(exc)
    code = STRATEGY_SEARCH_TIMEOUT if "timeout" in message.lower() else SOURCE_UNAVAILABLE
    return diagnostic(
        code,
        message,
        blocking=True,
        details={"case_name": context_name, "query": query},
    )


def case_evidence(
    strategy_case: StrategyCase,
    pokemon: dict[str, Any],
    moves_fetcher: FetchesPokemonMoves | None,
) -> dict[str, Any]:
    abilities = {item.get("name") for item in pokemon.get("abilities", [])}
    types = set(pokemon.get("types", []))
    stats = pokemon.get("stats", {})
    moves, pending = required_move_names(strategy_case, pokemon, moves_fetcher)
    evidence = []

    for rule in strategy_case.evidence_any:
        kind = rule["kind"]
        name = rule["name"]
        if kind == "ability" and name in abilities:
            evidence.append({"kind": "ability", "name": name})
        elif kind == "move" and name in moves:
            evidence.append({"kind": "move", "name": name})
        elif kind == "type" and name in types:
            evidence.append({"kind": "type", "name": name})
        elif kind == "stat_profile":
            stat_value = stat_value_for_rule(stats, rule["stat"])
            if stat_value >= int(rule["min"]):
                evidence.append({"kind": "stat_profile", "name": name, "value": stat_value})

    return {"matched": bool(evidence), "evidence": evidence, "pending": pending}


def required_move_names(
    strategy_case: StrategyCase,
    pokemon: dict[str, Any],
    moves_fetcher: FetchesPokemonMoves | None,
) -> tuple[set[str], list[str]]:
    needs_moves = any(rule.get("kind") == "move" for rule in strategy_case.evidence_any)
    if not needs_moves:
        return set(), []
    embedded = pokemon.get("moves")
    if embedded:
        return {
            move.get("name") or move.get("move", {}).get("name")
            for move in embedded
            if move.get("name") or move.get("move", {}).get("name")
        }, []
    if moves_fetcher is None:
        return set(), ["moves"]
    try:
        data = moves_fetcher.fetch_pokemon_moves(pokemon["name"])
    except RuntimeError:
        return set(), ["moves"]
    return {
        move.get("move", {}).get("name")
        for move in data.get("moves", [])
        if move.get("move", {}).get("name")
    }, []


def stat_value_for_rule(stats: dict[str, int | None], stat_name: str) -> int:
    if stat_name == "offense":
        return max(stats.get("attack") or 0, stats.get("special-attack") or 0)
    if stat_name == "bulk":
        return sum(stats.get(stat, 0) or 0 for stat in ("hp", "defense", "special-defense"))
    return stats.get(stat_name) or 0


def normalize_token(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    return normalized or None


def normalize_required_token(value: Any, field_name: str) -> str:
    normalized = normalize_token(value)
    if normalized is None:
        raise StrategyCaseError(INCOMPLETE_STRATEGY_CASE, f"{field_name} e obrigatorio.")
    return normalized


def normalize_types(raw_query: dict[str, Any]) -> tuple[str, ...]:
    raw_types = raw_query.get("types", raw_query.get("type"))
    if isinstance(raw_types, str):
        values = [raw_types]
    elif isinstance(raw_types, list):
        values = raw_types
    else:
        raise StrategyCaseError(INCOMPLETE_STRATEGY_CASE, "query types e obrigatoria.")
    types = tuple(normalize_required_token(item, "type") for item in values)
    if not types or len(types) > 2:
        raise StrategyCaseError(INVALID_STRATEGY_CASE, "query types deve conter um ou dois tipos.")
    return types


def normalize_min_value(raw: dict[str, Any]) -> int:
    value = raw.get("min", raw.get("min_value"))
    if not isinstance(value, int):
        raise StrategyCaseError(INCOMPLETE_STRATEGY_CASE, "min deve ser inteiro.")
    return value


def validate_stat(stat: str, raw: dict[str, Any]) -> None:
    if stat not in STAT_CHOICES:
        raise StrategyCaseError(
            UNSUPPORTED_STRATEGY_PREDICATE,
            f"Stat nao suportado: {stat}.",
            {"predicate": raw},
        )
