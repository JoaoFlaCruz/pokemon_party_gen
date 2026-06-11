"""Build a six-Pokemon team from user choices and ranked candidates."""

from __future__ import annotations

from typing import Any, Callable, Protocol

from mcp_server.src.application.use_cases.rank_pokemon import rank_pokemon
from mcp_server.src.infrastructure.pokeapi import PokemonFetcher, PokemonMovesFetcher

TEAM_SIZE = 6
TRIO_SIZE = 3
PRIMARY = "primary"
COMPLEMENTARY = "complementary"
DEFAULT_PRIMARY_STRATEGY = "balanced pressure"
DEFAULT_COMPLEMENTARY_STRATEGY = "complementary coverage"


class LooksUpPokemon(Protocol):
    def __call__(self, pokemon: str | int) -> dict[str, Any]:
        ...


class RanksCandidates(Protocol):
    def __call__(self, head_size: int) -> list[dict[str, Any]]:
        ...


def build_pokemon_team(
    pokemon: list[str | int] | None = None,
    primary_strategy: str | None = None,
    complementary_strategy: str | None = None,
    aces: list[str | int] | None = None,
    pokemon_lookup: LooksUpPokemon | None = None,
    candidate_ranker: RanksCandidates | None = None,
) -> dict[str, Any]:
    """Build a structured team response using validated data only."""
    normalized_pokemon, pending = normalize_selected_pokemon(pokemon)
    normalized_aces, ace_pending = normalize_aces(aces)
    pending.extend(ace_pending)

    lookup = pokemon_lookup or default_pokemon_lookup
    ranker = candidate_ranker or default_candidate_ranker
    members: list[dict[str, Any]] = []

    for requested in normalized_pokemon:
        try:
            details = lookup(requested)
        except Exception as exc:
            pending.append(
                pending_issue(
                    "unresolved-pokemon",
                    requested,
                    f"Pokemon informado pelo usuario nao foi validado: {exc}",
                )
            )
            continue

        members.append(
            make_member(
                details,
                source="user",
                locked=True,
                reason="Escolha informada pelo usuario.",
            )
        )

    if len(members) < TEAM_SIZE:
        try:
            candidates = ranker(max(TEAM_SIZE * 3, TEAM_SIZE - len(members)))
        except Exception as exc:
            candidates = []
            pending.append(
                pending_issue(
                    "candidate-data-unavailable",
                    None,
                    f"Nao foi possivel buscar candidatos validados: {exc}",
                )
            )

        add_candidates(members, candidates)

    if len(members) < TEAM_SIZE:
        pending.append(
            pending_issue(
                "insufficient-candidates",
                None,
                "Nao houve candidatos validados suficientes para completar 6 Pokemon.",
            )
        )

    members = members[:TEAM_SIZE]
    assign_trios_and_aces(members, normalized_aces)
    apply_roles(members)
    structure = {
        "primary_trio_strategy": clean_text(primary_strategy) or DEFAULT_PRIMARY_STRATEGY,
        "complementary_trio_strategy": (
            clean_text(complementary_strategy) or DEFAULT_COMPLEMENTARY_STRATEGY
        ),
    }

    unresolved_aces = [
        ace
        for ace in normalized_aces
        if not any(member["name"] == str(ace).strip().lower() for member in members)
    ]
    for ace in unresolved_aces:
        pending.append(
            pending_issue(
                "unresolved-ace",
                ace,
                "Ace informado nao foi encontrado entre os Pokemon validados do time.",
            )
        )

    return {
        "team_size": TEAM_SIZE,
        "is_complete": len(members) == TEAM_SIZE,
        "user_requested": [str(item).strip().lower() for item in normalized_pokemon],
        "team_structure": structure,
        "team": members,
        "analysis": build_analysis(members, structure),
        "pending": pending,
    }


def normalize_selected_pokemon(
    pokemon: list[str | int] | None,
) -> tuple[list[str | int], list[dict[str, Any]]]:
    """Normalize selected Pokemon, preserving first occurrence."""
    if not pokemon:
        return [], []

    normalized: list[str | int] = []
    pending: list[dict[str, Any]] = []
    seen: set[str] = set()
    unique_count = 0

    for item in pokemon:
        value = normalize_identifier(item)
        key = str(value)
        if key in seen:
            pending.append(
                pending_issue(
                    "duplicate-user-pokemon",
                    item,
                    "Pokemon repetido ignorado; a primeira ocorrencia foi preservada.",
                )
            )
            continue

        seen.add(key)
        unique_count += 1
        if unique_count > TEAM_SIZE:
            pending.append(
                pending_issue(
                    "team-size-limit",
                    item,
                    "Limite de 6 Pokemon aplicado; entradas extras foram ignoradas.",
                )
            )
            continue

        normalized.append(value)

    return normalized, pending


def normalize_aces(aces: list[str | int] | None) -> tuple[list[str | int], list[dict[str, Any]]]:
    if not aces:
        return [], []

    normalized: list[str | int] = []
    pending: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in aces:
        value = normalize_identifier(item)
        key = str(value)
        if key in seen:
            continue
        if len(normalized) >= 2:
            pending.append(
                pending_issue(
                    "ace-limit",
                    item,
                    "Apenas dois aces sao usados: um por trio.",
                )
            )
            continue
        seen.add(key)
        normalized.append(value)
    return normalized, pending


def normalize_identifier(value: str | int) -> str | int:
    if isinstance(value, int):
        if value < 1:
            raise ValueError("IDs de Pokemon devem ser inteiros maiores que zero.")
        return value
    if not isinstance(value, str):
        raise ValueError("Pokemon deve conter apenas strings ou inteiros.")
    normalized = value.strip().lower()
    if not normalized:
        raise ValueError("Nome de Pokemon nao pode ser vazio.")
    return normalized


def clean_text(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    return value.strip() or None


def pending_issue(kind: str, value: Any, reason: str) -> dict[str, Any]:
    return {"type": kind, "input": value, "reason": reason}


def default_pokemon_lookup(pokemon: str | int) -> dict[str, Any]:
    data = PokemonMovesFetcher().fetch_pokemon_moves(pokemon, max_workers=1)
    return data["pokemon"]


def default_candidate_ranker(head_size: int) -> list[dict[str, Any]]:
    return rank_pokemon(PokemonFetcher(), head_size=head_size)


def make_member(
    details: dict[str, Any],
    source: str,
    locked: bool,
    reason: str,
    replaces_gap: str | None = None,
) -> dict[str, Any]:
    name = str(details.get("name", "")).strip().lower()
    member = {
        "name": name,
        "source": source,
        "locked": locked,
        "role": "flex",
        "trio": None,
        "reason": reason,
        "notes": [],
    }
    if "id" in details:
        member["id"] = details["id"]
    if details.get("stats"):
        member["stats"] = details["stats"]
    if source == "ai":
        member["replaces_gap"] = replaces_gap or "completar vaga validada no time"
    return member


def add_candidates(
    members: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> None:
    selected_names = {member["name"] for member in members}
    for candidate in candidates:
        if len(members) >= TEAM_SIZE:
            return

        name = str(candidate.get("name", "")).strip().lower()
        if not name or name in selected_names:
            continue

        members.append(
            make_member(
                candidate,
                source="ai",
                locked=False,
                reason="Selecionado entre candidatos validados pelo ranking.",
                replaces_gap=gap_for_slot(len(members)),
            )
        )
        selected_names.add(name)


def gap_for_slot(index: int) -> str:
    if index == 0:
        return "ace principal"
    if index == TRIO_SIZE:
        return "ace complementar"
    if index < TRIO_SIZE:
        return "suporte do trio principal"
    return "suporte do trio complementar"


def assign_trios_and_aces(members: list[dict[str, Any]], aces: list[str | int]) -> None:
    place_aces(members, aces)
    for index, member in enumerate(members):
        member["trio"] = PRIMARY if index < TRIO_SIZE else COMPLEMENTARY
        if index in {0, TRIO_SIZE}:
            member["role"] = "ace"


def place_aces(members: list[dict[str, Any]], aces: list[str | int]) -> None:
    if not members:
        return

    if aces:
        move_identifier_to_index(members, aces[0], 0)
    if len(aces) > 1 and len(members) > TRIO_SIZE:
        move_identifier_to_index(members, aces[1], TRIO_SIZE)


def move_identifier_to_index(
    members: list[dict[str, Any]],
    identifier: str | int,
    target_index: int,
) -> None:
    key = str(identifier).strip().lower()
    for index, member in enumerate(members):
        if str(member.get("name", "")).lower() == key or str(member.get("id")) == key:
            member_to_move = members.pop(index)
            members.insert(min(target_index, len(members)), member_to_move)
            return


def apply_roles(members: list[dict[str, Any]]) -> None:
    for index, member in enumerate(members):
        if index in {0, TRIO_SIZE}:
            member["role"] = "ace"
            continue
        member["role"] = infer_role(member.get("stats", {}))


def infer_role(stats: dict[str, int | None]) -> str:
    attack = stat_value(stats, "attack")
    special_attack = stat_value(stats, "special-attack")
    defense = stat_value(stats, "defense")
    special_defense = stat_value(stats, "special-defense")
    speed = stat_value(stats, "speed")

    if speed >= 100:
        return "speed-control"
    if defense >= 100 and defense >= special_defense:
        return "physical-wall"
    if special_defense >= 100:
        return "special-wall"
    if attack > special_attack:
        return "physical-attacker"
    if special_attack > attack:
        return "special-attacker"
    return "flex"


def stat_value(stats: dict[str, int | None], stat_name: str) -> int:
    return stats.get(stat_name) or 0


def build_analysis(
    members: list[dict[str, Any]],
    structure: dict[str, str],
) -> dict[str, list[str]]:
    complete = len(members) == TEAM_SIZE
    return {
        "strengths": [
            "Preserva escolhas validadas do usuario.",
            "Completa seis membros com candidatos ranqueados." if complete else "Mantem dados parciais validados.",
        ],
        "trio_differences": [
            (
                f"Trio principal: {structure['primary_trio_strategy']}; "
                f"trio complementar: {structure['complementary_trio_strategy']}."
            )
        ],
        "trio_complementarity": [
            "Os trios separam dois planos de jogo para permitir rotas alternativas."
        ],
        "risks": [
            "Selecao inicial usa ranking de stats e nao simula matchups competitivos completos."
        ],
        "selection_criteria": [
            "Preservar escolhas do usuario.",
            "Evitar Pokemon duplicados.",
            "Preencher vagas restantes com candidatos validados em ordem deterministica.",
        ],
    }
