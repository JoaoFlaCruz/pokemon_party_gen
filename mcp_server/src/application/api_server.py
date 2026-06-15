"""Lightweight HTTP server wrapping Pokemon Party Gen use cases."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from typing import Any

from mcp_server.src.application.use_cases.build_team import build_pokemon_team
from mcp_server.src.application.use_cases.rank_pokemon import rank_pokemon
from mcp_server.src.application.use_cases.rank_moveset import rank_pokemon_moveset
from mcp_server.src.infrastructure.pokeapi import PokemonFetcher, TypeRelationsFetcher


class PokemonApiHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

    def write_json_response(self, status: int, data: Any):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.wfile.write(response_bytes)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        try:
            if path == "/api/rankings":
                types = query.get("type", None)
                offense_stat = query.get("offense_stat", ["auto"])[0]
                priority_stat = query.get("priority_stat", [None])[0]
                speed_mode = query.get("speed_mode", ["ignore"])[0]
                head_size_str = query.get("head_size", ["10"])[0]

                try:
                    head_size = int(head_size_str)
                except ValueError:
                    self.write_json_response(400, {"error": "head_size deve ser um número inteiro."})
                    return

                fetcher = PokemonFetcher()
                result = rank_pokemon(
                    fetcher=fetcher,
                    types=types,
                    offense_stat=offense_stat,
                    priority_stat=priority_stat,
                    speed_mode=speed_mode,
                    head_size=head_size
                )
                self.write_json_response(200, result)

            elif path == "/api/moves":
                pokemon = query.get("pokemon", [None])[0]
                if not pokemon:
                    self.write_json_response(400, {"error": "Query param 'pokemon' é obrigatório."})
                    return

                result = rank_pokemon_moveset(pokemon)
                self.write_json_response(200, result)

            elif path == "/api/types":
                pokemon_type = query.get("type", [None])[0]
                if not pokemon_type:
                    self.write_json_response(400, {"error": "Query param 'type' é obrigatório."})
                    return

                fetcher = TypeRelationsFetcher()
                result = fetcher.fetch_type_relations(pokemon_type)
                self.write_json_response(200, result)

            else:
                self.write_json_response(404, {"error": "Rota não encontrada."})

        except Exception as exc:
            self.write_json_response(500, {"error": str(exc)})

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        try:
            if path == "/api/build-team":
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length == 0:
                    body = {}
                else:
                    body_bytes = self.rfile.read(content_length)
                    body = json.loads(body_bytes.decode("utf-8"))

                pokemon = body.get("pokemon")
                primary_strategy = body.get("primary_strategy")
                complementary_strategy = body.get("complementary_strategy")
                aces = body.get("aces")

                result = build_pokemon_team(
                    pokemon=pokemon,
                    primary_strategy=primary_strategy,
                    complementary_strategy=complementary_strategy,
                    aces=aces
                )
                self.write_json_response(200, result)
            else:
                self.write_json_response(404, {"error": "Rota não encontrada."})

        except json.JSONDecodeError:
            self.write_json_response(400, {"error": "JSON inválido."})
        except Exception as exc:
            self.write_json_response(500, {"error": str(exc)})


def run_server(port: int = 8002):
    server_address = ("", port)
    httpd = HTTPServer(server_address, PokemonApiHandler)
    print(f"Servidor API rodando na porta {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor finalizado.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
