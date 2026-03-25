"""MCP (Model Context Protocol) client for connecting to external tools.

This provides a basic MCP client that can connect to MCP servers.
"""

import json
import logging
import asyncio
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP client for connecting to MCP servers."""

    def __init__(self):
        self.servers = {}
        self.tools = {}

    def add_server(self, name: str, command: List[str], env: Optional[Dict] = None):
        """Add an MCP server.

        Args:
            name: Server name
            command: Command to start server (e.g., ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/path"])
            env: Environment variables
        """
        self.servers[name] = {
            "command": command,
            "env": env or {},
            "process": None,
        }
        logger.info(f"Added MCP server: {name}")

    async def connect(self, name: str) -> bool:
        """Connect to an MCP server."""
        if name not in self.servers:
            logger.error(f"Unknown MCP server: {name}")
            return False

        server = self.servers[name]
        try:
            # Start the MCP server process
            process = await asyncio.create_subprocess_exec(
                *server["command"],
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, **server["env"]} if server["env"] else None,
            )
            server["process"] = process
            logger.info(f"Connected to MCP server: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {name}: {e}")
            return False

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict) -> Any:
        """Call a tool on an MCP server.

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result
        """
        if server_name not in self.servers:
            return {"error": f"Unknown server: {server_name}"}

        server = self.servers[server_name]
        if not server.get("process"):
            await self.connect(server_name)

        # MCP JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        try:
            process = server["process"]
            request_json = json.dumps(request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()

            # Read response
            response_line = await process.stdout.readline()
            response = json.loads(response_line)

            if "error" in response:
                return {"error": response["error"]}
            return response.get("result", {})
        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            return {"error": str(e)}

    async def list_tools(self, server_name: str) -> List[Dict]:
        """List available tools on an MCP server."""
        if server_name not in self.servers:
            return []

        server = self.servers[server_name]
        if not server.get("process"):
            await self.connect(server_name)

        request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}

        try:
            process = server["process"]
            request_json = json.dumps(request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()

            response_line = await process.stdout.readline()
            response = json.loads(response_line)

            return response.get("result", {}).get("tools", [])
        except Exception as e:
            logger.error(f"Failed to list MCP tools: {e}")
            return []

    async def disconnect(self, name: str):
        """Disconnect from an MCP server."""
        if name in self.servers and self.servers[name].get("process"):
            self.servers[name]["process"].terminate()
            await self.servers[name]["process"].wait()
            logger.info(f"Disconnected from MCP server: {name}")


# Global MCP client instance
_mcp_client = None


def get_mcp_client() -> MCPClient:
    """Get the global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


def register_mcp_servers():
    """Register MCP servers from environment or config."""
    import os

    client = get_mcp_client()

    # Check for MCP server configurations
    mcp_servers = os.environ.get("ANDILE_MCP_SERVERS", "")
    if mcp_servers:
        for server_config in mcp_servers.split(","):
            parts = server_config.strip().split(":")
            if len(parts) >= 2:
                name = parts[0]
                command = parts[1].split()
                client.add_server(name, command)
                logger.info(f"Registered MCP server: {name}")
