"""AI Agent orchestrator executing a ReAct loop with local Pokemon tools."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any

from mcp_server.src.config.env import POKEAPI_BASE_URL
from mcp_server.src.application.use_cases.build_team import build_pokemon_team
from mcp_server.src.application.use_cases.rank_pokemon import rank_pokemon
from mcp_server.src.application.use_cases.rank_moveset import rank_pokemon_moveset
from mcp_server.src.infrastructure.pokeapi import ItemFetcher, TypeRelationsFetcher
from mcp_server.src.mcp.tools.banned_pokemon_tool import execute_ban_pokemon_tool
from mcp_server.src.mcp.tools.champions_legality_tool import execute_champions_legality_tool


SYSTEM_PROMPT = """Você é um Estrategista e Assistente de Batalha Pokémon profissional.
Seu objetivo é ajudar o usuário com dúvidas de Pokémon, análises de golpes (movesets), classificação (rankings) e, principalmente, montagem de times de 6 Pokémon.

Você tem acesso a um conjunto de ferramentas locais. Quando o usuário fizer uma pergunta, você pode decidir chamar uma ou mais ferramentas para obter dados reais do banco de dados local antes de responder.
Você deve planejar suas ações passo a passo no formato ReAct.

FERRAMENTAS DISPONÍVEIS:

1. `build_pokemon_team`
   - Descrição: Monta/completa um time de 6 Pokémon.
   - Parâmetros:
     - `pokemon` (lista de strings/inteiros, opcional): Pokémon que devem estar fixos no time.
     - `aces` (lista de strings/inteiros, opcional, max 2): Pokémon líderes/aces de cada trio.
     - `primary_strategy` (string, opcional): Estratégia do trio principal.
     - `complementary_strategy` (string, opcional): Estratégia do trio complementar.

2. `rank_pokemon`
   - Descrição: Classifica e ordena os melhores Pokémon com base em critérios de atributos básicos.
   - Parâmetros:
     - `types` (lista de strings, opcional, max 2): Filtrar por tipo (ex: ["fire", "flying"]).
     - `offense_stat` (string, opcional, padrão: "auto"): Forçar atributo ofensivo ("attack" ou "special-attack" ou "auto").
     - `priority_stat` (string, opcional): Atributo com peso 1.4 no cálculo (ex: "hp", "defense", "speed").
     - `speed_mode` (string, opcional, padrão: "ignore"): Como avaliar velocidade ("ignore", "high", "low").
     - `head_size` (inteiro, opcional, padrão: 10): Quantidade máxima de resultados.
     - `champions_only` (booleano, opcional, padrão: false): Restringir à Pokédex Champions.

3. `rank_pokemon_moveset`
   - Descrição: Retorna e classifica os melhores ataques/movimentos sugeridos para um Pokémon.
   - Parâmetros:
     - `pokemon` (string ou inteiro, obrigatório): Nome ou ID do Pokémon.

4. `list_items`
   - Descrição: Lista os itens Pokémon disponíveis com custo, categoria e efeitos.
   - Parâmetros:
     - `limit` (inteiro, opcional, padrão: 20, max 100): Limite de resultados.
     - `offset` (inteiro, opcional, padrão: 0): Paginação.

5. `get_type_relations`
   - Descrição: Busca fraquezas, imunidades e resistências de um tipo Pokémon.
   - Parâmetros:
     - `type` (string ou inteiro, obrigatório): Nome ou ID do tipo (ex: "fire").

6. `ban_pokemon`
   - Descrição: Registra um Pokémon proibido/banido para exclusão em rankings locais.
   - Parâmetros:
     - `id` (inteiro, obrigatório): ID do Pokémon.
     - `name` (string, obrigatório): Nome do Pokémon.

7. `validate_champions_legality`
   - Descrição: Valida a legalidade de um Pokémon, golpe, habilidade ou item contra as regras do formato Champions.
   - Parâmetros:
     - `entity_type` (string, obrigatório): "pokemon", "move", "ability" ou "item".
     - `entity` (string/inteiro, obrigatório): Nome ou ID da entidade.
     - `pokemon` (string/inteiro, opcional): Pokémon relacionado se validando move/ability.

FORMATO DE RESPOSTA OBRIGATÓRIO:
Você deve responder APENAS com um objeto JSON válido. Não inclua textos antes ou depois do JSON (não use ```json ... ```, responda puramente o texto JSON cru).

Se precisar chamar uma ferramenta:
{
  "thought": "Seu raciocínio em português de por que precisa dessa ferramenta.",
  "action": "call_tool",
  "tool": "nome_da_ferramenta",
  "arguments": { ... }
}

Se tiver todas as informações para responder ou se tiver terminado de processar o time:
{
  "thought": "Seu raciocínio final.",
  "action": "done",
  "response": "Sua resposta final em português explicando os detalhes, estratégias e análises.",
  "team_data": { ... } // OPCIONAL: Inclua os dados brutos de retorno do 'build_pokemon_team' se você gerou ou atualizou o time.
}

Observação Importante: Ao responder, fale sempre em português (Brasil). Seja analítico, estratégico e profissional.
"""


def execute_local_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute local business logic/data fetchers by tool name."""
    try:
        if name == "build_pokemon_team":
            return build_pokemon_team(
                pokemon=arguments.get("pokemon"),
                primary_strategy=arguments.get("primary_strategy"),
                complementary_strategy=arguments.get("complementary_strategy"),
                aces=arguments.get("aces"),
            )
        elif name == "rank_pokemon":
            from mcp_server.src.infrastructure.pokeapi import PokemonFetcher
            return {
                "rankings": rank_pokemon(
                    fetcher=PokemonFetcher(),
                    types=arguments.get("types"),
                    offense_stat=arguments.get("offense_stat", "auto"),
                    priority_stat=arguments.get("priority_stat"),
                    speed_mode=arguments.get("speed_mode", "ignore"),
                    head_size=arguments.get("head_size", 10),
                    champions_only=arguments.get("champions_only", False),
                )
            }
        elif name == "rank_pokemon_moveset":
            return rank_pokemon_moveset(
                pokemon=arguments.get("pokemon"),
            )
        elif name == "list_items":
            return ItemFetcher().fetch_items(
                limit=arguments.get("limit", 20),
                offset=arguments.get("offset", 0),
            )
        elif name == "get_type_relations":
            return TypeRelationsFetcher().fetch_type_relations(
                pokemon_type=arguments.get("type"),
            )
        elif name == "ban_pokemon":
            return execute_ban_pokemon_tool(arguments)
        elif name == "validate_champions_legality":
            return execute_champions_legality_tool(arguments)
        else:
            return {"error": f"Tool {name} desconhecida."}
    except Exception as exc:
        return {"error": str(exc)}


def request_llm(
    provider: str,
    system_prompt: str,
    history: list[dict[str, Any]],
) -> str:
    """Send request to the chosen LLM API using standard urllib."""
    provider = provider.lower().strip()
    
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Chave GEMINI_API_KEY não encontrada no ambiente/.env")
        
        # Format for Gemini API (generateContent)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        # Convert history format to Gemini parts
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": contents,
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw_response = json.loads(resp.read().decode("utf-8"))
            
        try:
            return raw_response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Formato de resposta inesperado do Gemini: {raw_response}") from exc

    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Chave OPENAI_API_KEY não encontrada no ambiente/.env")
            
        url = "https://api.openai.com/v1/chat/completions"
        
        # Convert history format
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "response_format": {"type": "json_object"}
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw_response = json.loads(resp.read().decode("utf-8"))
            
        try:
            return raw_response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Formato de resposta inesperado da OpenAI: {raw_response}") from exc

    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Chave ANTHROPIC_API_KEY não encontrada no ambiente/.env")
            
        url = "https://api.anthropic.com/v1/messages"
        
        # Anthropic messages format (roles: user, assistant)
        messages = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
            
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": messages
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw_response = json.loads(resp.read().decode("utf-8"))
            
        try:
            return raw_response["content"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Formato de resposta inesperado da Anthropic: {raw_response}") from exc

    else:
        raise ValueError(f"Provedor de IA desconhecido: {provider}")


def run_agent_loop(
    message: str,
    provider: str,
    current_team: list[str | int] | None = None,
) -> dict[str, Any]:
    """Execute the ReAct agent loop using tools on behalf of the AI."""
    print(f"[AI Agent] Iniciando loop com provedor={provider}, mensagem='{message}'")
    
    # Enrich the first message with context about the current team, if any
    enriched_message = message
    if current_team:
        enriched_message = f"Time atual na tela: {current_team}.\nUsuário diz: {message}"
        
    history = [{"role": "user", "content": enriched_message}]
    max_steps = 10
    last_team_data = None
    
    for step in range(max_steps):
        print(f"[AI Agent] Passo {step + 1}...")
        try:
            llm_text = request_llm(provider, SYSTEM_PROMPT, history)
        except Exception as exc:
            print(f"[AI Agent] Erro na requisição LLM: {exc}")
            return {
                "response": f"Desculpe, ocorreu um erro de conexão com a IA ({provider}): {exc}",
                "team_data": None
            }
            
        print(f"[AI Agent] Resposta do LLM:\n{llm_text}")
        
        # Clean response (sometimes models add markdown formatting codeblocks despite instructions)
        cleaned_text = llm_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        try:
            response_json = json.loads(cleaned_text)
        except json.JSONDecodeError as exc:
            print(f"[AI Agent] Resposta não era um JSON válido: {exc}")
            return {
                "response": "Desculpe, a IA retornou um formato de resposta inválido que não pôde ser interpretado.",
                "team_data": None
            }
            
        action = response_json.get("action")
        thought = response_json.get("thought", "")
        
        if action == "call_tool":
            tool_name = response_json.get("tool")
            tool_args = response_json.get("arguments", {})
            print(f"[AI Agent] Pensamento: {thought}")
            print(f"[AI Agent] Chamando ferramenta local: {tool_name} com arguments: {tool_args}")
            
            tool_result = execute_local_tool(tool_name, tool_args)
            
            # Save team_data if we called build_pokemon_team
            if tool_name == "build_pokemon_team" and "error" not in tool_result:
                last_team_data = tool_result
                
            # Add to history
            history.append({"role": "model", "content": llm_text})
            history.append({
                "role": "user",
                "content": f"Resultado da ferramenta {tool_name}: {json.dumps(tool_result, ensure_ascii=False)}"
            })
            
        elif action == "done":
            print(f"[AI Agent] Loop concluído. Pensamento final: {thought}")
            final_response = response_json.get("response", "Pronto.")
            team_data = response_json.get("team_data") or last_team_data
            
            return {
                "response": final_response,
                "team_data": team_data
            }
        else:
            print(f"[AI Agent] Ação desconhecida: {action}")
            return {
                "response": "Desculpe, a IA executou uma ação não suportada.",
                "team_data": None
            }
            
    print("[AI Agent] Limite máximo de passos atingido.")
    return {
        "response": "O assistente de IA atingiu o limite de reflexão antes de concluir a resposta.",
        "team_data": last_team_data
    }
