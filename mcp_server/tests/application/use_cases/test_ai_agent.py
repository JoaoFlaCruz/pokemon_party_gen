"""Tests for the AI Agent Orchestrator and ReAct loop."""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from mcp_server.src.application.ai_agent import run_agent_loop, execute_local_tool


def make_mock_response(data: dict[str, Any]) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(data).encode("utf-8")
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_resp
    return mock_ctx


class AIAgentTests(unittest.TestCase):

    @patch("mcp_server.src.application.ai_agent.build_pokemon_team")
    @patch("urllib.request.urlopen")
    @patch("os.getenv")
    def test_run_agent_loop_gemini_success(self, mock_getenv: MagicMock, mock_urlopen: MagicMock, mock_build_team: MagicMock) -> None:
        # Mock team builder return value
        mock_build_team.return_value = {
            "is_complete": True,
            "team": [{"name": "charizard", "source": "user"}]
        }
        # Mock API Key
        mock_getenv.side_effect = lambda name: "fake_gemini_key" if name == "GEMINI_API_KEY" else None

        # Prepare mock HTTP response for Gemini
        turn1_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "thought": "Preciso montar um time com Charizard.",
                            "action": "call_tool",
                            "tool": "build_pokemon_team",
                            "arguments": {"pokemon": ["charizard"]}
                        })
                    }]
                }
            }]
        }
        
        turn2_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "thought": "Pronto, time montado.",
                            "action": "done",
                            "response": "Time de fogo gerado com sucesso!",
                            "team_data": {"is_complete": True, "team": [{"name": "charizard", "source": "user"}]}
                        })
                    }]
                }
            }]
        }

        mock_urlopen.side_effect = [
            make_mock_response(turn1_response),
            make_mock_response(turn2_response)
        ]

        # Run loop
        result = run_agent_loop(
            message="Monte um time com Charizard",
            provider="gemini"
        )

        self.assertEqual(result["response"], "Time de fogo gerado com sucesso!")
        self.assertIsNotNone(result["team_data"])
        self.assertTrue(result["team_data"]["is_complete"])
        self.assertEqual(result["team_data"]["team"][0]["name"], "charizard")

    @patch("urllib.request.urlopen")
    @patch("os.getenv")
    def test_run_agent_loop_openai_success(self, mock_getenv: MagicMock, mock_urlopen: MagicMock) -> None:
        mock_getenv.side_effect = lambda name: "fake_openai_key" if name == "OPENAI_API_KEY" else None

        openai_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "thought": "Vou responder diretamente.",
                        "action": "done",
                        "response": "Olá! Como posso ajudar?"
                    })
                }
            }]
        }

        mock_urlopen.return_value = make_mock_response(openai_response)

        result = run_agent_loop(
            message="Olá",
            provider="openai"
        )

        self.assertEqual(result["response"], "Olá! Como posso ajudar?")
        self.assertIsNone(result["team_data"])

    @patch("urllib.request.urlopen")
    @patch("os.getenv")
    def test_run_agent_loop_anthropic_success(self, mock_getenv: MagicMock, mock_urlopen: MagicMock) -> None:
        mock_getenv.side_effect = lambda name: "fake_anthropic_key" if name == "ANTHROPIC_API_KEY" else None

        anthropic_response = {
            "content": [{
                "text": json.dumps({
                    "thought": "Vou responder diretamente com Claude.",
                    "action": "done",
                    "response": "Olá do Claude!"
                })
            }]
        }

        mock_urlopen.return_value = make_mock_response(anthropic_response)

        result = run_agent_loop(
            message="Olá",
            provider="anthropic"
        )

        self.assertEqual(result["response"], "Olá do Claude!")

    def test_execute_local_tool_invalid(self) -> None:
        result = execute_local_tool("unknown_tool", {})
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
