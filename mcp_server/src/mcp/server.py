"""Minimal MCP stdio server exposing Pokemon tools to Codex."""

from __future__ import annotations

import json
import sys
from typing import Any

from mcp_server.src.mcp.tools.banned_pokemon_tool import BAN_POKEMON_TOOL, execute_ban_pokemon_tool
from mcp_server.src.mcp.tools.item_tool import ITEM_TOOL, execute_item_tool
from mcp_server.src.mcp.tools.pokemon_moveset_tool import POKEMON_MOVESET_TOOL, execute_pokemon_moveset_tool
from mcp_server.src.mcp.tools.pokemon_ranking_tool import POKEMON_RANKING_TOOL, execute_pokemon_ranking_tool
from mcp_server.src.mcp.tools.type_relations_tool import TYPE_RELATIONS_TOOL, execute_type_relations_tool

JSONRPC_VERSION = "2.0"
DEFAULT_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "pokemon-tools"
SERVER_VERSION = "0.1.0"


TOOLS = {
    BAN_POKEMON_TOOL["function"]["name"]: (
        BAN_POKEMON_TOOL,
        execute_ban_pokemon_tool,
    ),
    ITEM_TOOL["function"]["name"]: (
        ITEM_TOOL,
        execute_item_tool,
    ),
    POKEMON_MOVESET_TOOL["function"]["name"]: (
        POKEMON_MOVESET_TOOL,
        execute_pokemon_moveset_tool,
    ),
    POKEMON_RANKING_TOOL["function"]["name"]: (
        POKEMON_RANKING_TOOL,
        execute_pokemon_ranking_tool,
    ),
    TYPE_RELATIONS_TOOL["function"]["name"]: (
        TYPE_RELATIONS_TOOL,
        execute_type_relations_tool,
    ),
}


def tool_definition(tool: dict[str, Any] = POKEMON_MOVESET_TOOL) -> dict[str, Any]:
    function = tool["function"]
    return {
        "name": function["name"],
        "description": function["description"],
        "inputSchema": function["parameters"],
    }


def tool_definitions() -> list[dict[str, Any]]:
    return [tool_definition(tool) for tool, _executor in TOOLS.values()]


def handle_message(message: dict[str, Any]) -> dict[str, Any] | None:
    """Handle one JSON-RPC MCP message."""
    method = message.get("method")
    request_id = message.get("id")

    if request_id is None:
        return None

    try:
        result = dispatch(method, message.get("params") or {})
        return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}
    except ValueError as exc:
        return error_response(request_id, -32602, str(exc))
    except NotImplementedError as exc:
        return error_response(request_id, -32601, str(exc))
    except Exception as exc:  # pragma: no cover - keeps server failures JSON-RPC shaped.
        return error_response(request_id, -32000, str(exc))


def dispatch(method: str | None, params: dict[str, Any]) -> dict[str, Any]:
    if method == "initialize":
        protocol_version = params.get("protocolVersion") or DEFAULT_PROTOCOL_VERSION
        return {
            "protocolVersion": protocol_version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": (
                "Use ban_pokemon para registrar Pokemon proibidos no banco de exclusao. "
                "Use get_type_relations quando o usuario pedir relacoes, fraquezas, "
                "imunidades ou efetividade entre tipos. Use list_items quando o usuario "
                "pedir itens Pokemon, descricoes de itens ou validacao geral de itens. "
                "Use rank_pokemon para rankings de Pokemon por stats e filtros de tipo. "
                "Use rank_pokemon_moveset quando o usuario pedir ranking, moveset, "
                "melhores golpes ou analise ofensiva de um Pokemon por nome ou ID."
            ),
        }

    if method == "ping":
        return {}

    if method == "tools/list":
        return {"tools": tool_definitions()}

    if method == "tools/call":
        return call_tool(params)

    raise NotImplementedError(f"Metodo MCP nao suportado: {method}")


def call_tool(params: dict[str, Any]) -> dict[str, Any]:
    name = params.get("name")
    if name not in TOOLS:
        raise ValueError(f"Tool desconhecida: {name}")

    arguments = params.get("arguments") or {}
    if not isinstance(arguments, dict):
        raise ValueError("arguments deve ser um objeto JSON.")

    _tool, executor = TOOLS[name]
    result = executor(arguments)
    return {
        "content": [
            {"type": "text", "text": result["presentation"]},
            {
                "type": "text",
                "text": json.dumps(result["data"], indent=2, ensure_ascii=False),
            },
        ],
        "structuredContent": result,
    }


def error_response(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": JSONRPC_VERSION,
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue

        try:
            message = json.loads(line)
            response = handle_message(message)
        except json.JSONDecodeError as exc:
            response = error_response(None, -32700, f"JSON invalido: {exc}")

        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
