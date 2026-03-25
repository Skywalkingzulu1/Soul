#!/usr/bin/env python3
"""Simple API server for Andile Dashboard"""

import json
import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Use absolute paths for reliability
BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
ORCHESTRATION_PATH = KNOWLEDGE_DIR / "orchestration.json"

# Ensure knowledge directory exists
KNOWLEDGE_DIR.mkdir(exist_ok=True)

# Simple API token from environment (dev default if not set)
API_TOKEN = os.getenv("ANDILE_API_TOKEN", "andile_dev_secret_2026")


def load_orchestration():
    """Load orchestration state with error handling."""
    if ORCHESTRATION_PATH.exists():
        try:
            with open(ORCHESTRATION_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"error": "Corrupted orchestration.json"}
    return {"error": "orchestration.json not found"}


def check_auth(handler) -> bool:
    """Check if request has valid auth token."""
    auth_header = handler.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        return token == API_TOKEN
    return False


class APIHandler(SimpleHTTPRequestHandler):
    """API Handler with CORS and authentication support."""

    def _send_cors_headers(self):
        """Add CORS headers to response."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/api/andile-think":
            # Check auth
            if not check_auth(self):
                self.send_response(401)
                self._send_cors_headers()
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return

            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-type", "application/json")
            self.end_headers()

            query = parse_qs(urlparse(self.path).query)
            prompt = query.get("prompt", ["What should I do next to make money?"])[0]

            try:
                from soul.orchestration import AndileCloud

                andile = AndileCloud()
                thought = andile.think(prompt)
                self.wfile.write(
                    json.dumps({"success": True, "thought": thought}).encode()
                )
            except Exception as e:
                self.wfile.write(
                    json.dumps({"success": False, "error": str(e)}).encode()
                )
            return

        elif self.path == "/api/status":
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-type", "application/json")
            self.end_headers()

            data = load_orchestration()
            self.wfile.write(json.dumps(data).encode())
            return

        elif self.path == "/api/tasks":
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-type", "application/json")
            self.end_headers()

            data = load_orchestration()
            tasks = data.get("tasks", []) if isinstance(data, dict) else []
            pending = [t for t in tasks if t.get("status") == "pending"]
            self.wfile.write(json.dumps(pending).encode())
            return

        elif self.path == "/api/health":
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {"status": "healthy", "api_token_set": bool(API_TOKEN)}
                ).encode()
            )
            return

        # Serve static files from base directory
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/api/think":
            # Check auth
            if not check_auth(self):
                self.send_response(401)
                self._send_cors_headers()
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return

            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            prompt = data.get("prompt", "What should I do?")

            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-type", "application/json")
            self.end_headers()

            try:
                from soul.orchestration import AndileCloud

                andile = AndileCloud()
                thought = andile.think(prompt)
                self.wfile.write(
                    json.dumps({"success": True, "thought": thought}).encode()
                )
            except Exception as e:
                self.wfile.write(
                    json.dumps({"success": False, "error": str(e)}).encode()
                )
            return

    def translate_path(self, path: str) -> str:
        """Translate URL path to filesystem path, serving from BASE_DIR."""
        # Remove leading slash
        path = path.split("?", 1)[0]
        path = path.lstrip("/")

        # Default to index.html for root
        if not path:
            path = "index.html"

        return str(BASE_DIR / path)


def run_server(port: int = 8090):
    """Run the API server."""
    server = HTTPServer(("", port), APIHandler)
    print(f"Andile API server running on http://localhost:{port}")
    print(f"API Token: {'*' * 20}{API_TOKEN[-8:]}")
    print(f"Health check: http://localhost:{port}/api/health")
    server.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    run_server(port)
