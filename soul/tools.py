import subprocess
import sys
import logging
import asyncio
import json

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Pluggable tools the soul can use to interact with the world."""

    def __init__(self) -> None:
        self.tools = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register("search", WebSearchTool())
        self.register("code", CodeExecutor())
        self.register("browser", None)  # Lazy-loaded in brain.py

        # Codebase analysis tools (like Gemini CLI)
        self.register("glob", GlobTool())
        self.register("grep", GrepTool())
        self.register("read_file", ReadFileTool())
        self.register("write_file", WriteFileTool())
        self.register("ls", ListDirTool())

        # Super Agent tools
        from soul.os_automation import OSAutomation
        from soul.shell_tool import ShellTool
        from soul.youtube import YouTubeTool
        from soul.cloud import ImpossibleCloud
        from soul.bunny_cloud import BunnyMagicContainers

        self.register("os", OSAutomation())
        self.register("shell", ShellTool())
        self.register("stealth_stream", StealthStreamerTool())
        self.register("youtube", YouTubeTool())
        self.register("cloud", CloudTool())
        self.register("bunny", BunnyCloudTool())

    def register(self, name, tool) -> None:
        self.tools[name] = tool

    async def execute(self, tool_name, *args, **kwargs) -> None:
        tool = self.tools.get(tool_name)
        if tool is None:
            return f"Tool '{tool_name}' is not available."

        timeout = kwargs.pop("timeout", 60)  # Default 60s hard timeout

        try:
            if asyncio.iscoroutinefunction(tool.execute):
                return await asyncio.wait_for(
                    tool.execute(*args, **kwargs), timeout=timeout
                )

            # Run sync tools in executor to prevent blocking the event loop
            loop = asyncio.get_event_loop()
            return await asyncio.wait_for(
                loop.run_in_executor(None, lambda: tool.execute(*args, **kwargs)),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.error(f"Tool '{tool_name}' timed out after {timeout}s.")
            return f"Error: Tool execution timed out after {timeout} seconds."
        except Exception as e:
            logger.error(f"Tool '{tool_name}' failed: {e}")
            return f"Tool error: {e}"

    def describe(self) -> None:
        desc = "AVAILABLE TOOLS:\n"
        for name, tool in self.tools.items():
            if tool:
                desc += f"- {name}: {tool.description}\n"
            else:
                desc += f"- {name}: (not loaded)\n"
        return desc


class WebSearchTool:
    description = "Search the web using DuckDuckGo. Input: search query string."

    def execute(self, query, max_results=5) -> None:
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            results = []
            ddgs = DDGS()
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"- {r['title']}: {r['body']}\n  {r['href']}")
            if results:
                return "SEARCH RESULTS:\n" + "\n".join(results)
            return "No results found."
        except Exception as e:
            return f"Search failed: {e}"


class CodeExecutor:
    description = (
        "Execute Python code in a sandboxed subprocess. Input: Python code string."
    )

    # Blocked patterns for dangerous operations
    BLOCKED_PATTERNS = [
        "import os",
        "import sys",
        "import subprocess",
        "import socket",
        "import requests",
        "import httpx",
        "import urllib",
        "open(",
        "file(",
        "eval(",
        "exec(",
        "__import__",
        "compile(",
        "pickle",
        "marshal",
        " shelve",
        "stdio",
        "stdout",
        "stderr",
        "stdin",
    ]

    def execute(self, code, timeout=15) -> None:
        # Basic safety check
        code_lower = code.lower()
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.lower() in code_lower:
                return f"Security: Blocked dangerous pattern '{pattern}' in code. This tool is for safe calculations only."

        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}"
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            return output.strip() or "Code executed with no output."
        except subprocess.TimeoutExpired:
            return f"Code execution timed out after {timeout}s"
        except Exception as e:
            return f"Execution error: {e}"


class StealthStreamerTool:
    description = (
        "Advanced stealth browser for streaming and bypassing anti-bot. "
        "Blocks ads, popups and sniffs for video URLs. Input: URL string."
    )

    async def execute(self, url) -> None:
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth
        import re

        async with async_playwright() as p:
            # Launch with stealth-optimized args
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                ],
            )

            context = await browser.new_context(
                viewport=None,
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            )

            page = await context.new_page()
            await Stealth().apply_stealth_async(page)

            # 1. Programmatic Ad-Blocking via Request Interception
            ad_patterns = [
                re.compile(pattern)
                for pattern in [
                    r".*doubleclick\.net.*",
                    r".*adservice\.google.*",
                    r".*adnxs\.com.*",
                    r".*popads\.net.*",
                    r".*propellerads\.com.*",
                    r".*a-ads\.com.*",
                    r".*onclickads\.net.*",
                    r".*ad-delivery\.net.*",
                    r".*vidverto\.io.*",
                ]
            ]

            async def intercept(route) -> None:
                if any(p.match(route.request.url) for p in ad_patterns):
                    return await route.abort()
                await route.continue_()

            await page.route("**/*", intercept)

            # Close popups as soon as they spawn
            context.on("page", lambda new_page: asyncio.create_task(new_page.close()))

            # 2. Network Sniffing for Video Sources
            video_sources = []

            def handle_response(response) -> None:
                u = response.url
                if ".m3u8" in u or ".mp4" in u or "googlevideo.com" in u:
                    if u not in video_sources:
                        video_sources.append(u)

            page.on("response", handle_response)

            logger.info(f"Stealth-navigating to {url}...")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(10)  # Let stream buffer

                # Check for video and try to play if not autostarted
                await page.click(
                    "video, .play-button, .vjs-big-play-button", timeout=5000
                )
                await asyncio.sleep(3)
            except Exception:
                pass

            status = (
                "Playback started (confirmed by sniff)"
                if video_sources
                else "Stealth applied, check UI."
            )
            source_info = (
                f"\nSources found: {len(video_sources)}" if video_sources else ""
            )

            # Keep open for a bit to allow the user to watch
            await asyncio.sleep(120)
            await browser.close()

            return f"{status}{source_info}"


class CloudTool:
    description = "Manage cloud infrastructure (Impossible Cloud). Commands: status, contracts, partners."

    def execute(self, command) -> None:
        from soul.cloud import ImpossibleCloud

        cloud = ImpossibleCloud()

        cmd = command.lower().strip()
        if cmd == "status":
            return cloud.get_status()
        elif cmd == "contracts":
            return json.dumps(cloud.list_contracts(), indent=2)
        elif cmd == "partners":
            return json.dumps(cloud.list_partners(), indent=2)
        else:
            return (
                f"Unknown cloud command: {command}. Try: status, contracts, partners."
            )


class BunnyCloudTool:
    description = "Manage Bunny.net Magic Containers. Commands: status, apps, regions, deploy <name> <image>, update <id> <image>."

    def execute(self, command) -> None:
        from soul.bunny_cloud import BunnyMagicContainers

        bunny = BunnyMagicContainers()

        parts = command.split(" ")
        cmd = parts[0].lower().strip()

        if cmd == "status":
            return "Bunny.net Magic Containers API is reachable."
        elif cmd == "apps":
            apps = bunny.list_apps()
            return json.dumps(apps, indent=2)
        elif cmd == "regions":
            regions = bunny.list_regions()
            return json.dumps(regions, indent=2)
        elif cmd == "deploy":
            if len(parts) < 3:
                return "Usage: deploy <name> <image>"
            name = parts[1]
            image = parts[2]
            res = bunny.create_app(name, image)
            return json.dumps(res, indent=2)
        elif cmd == "update":
            if len(parts) < 3:
                return "Usage: update <app_id> <image>"
            res = bunny.update_app(parts[1], parts[2])
            return json.dumps(res, indent=2)
        elif cmd == "get":
            if len(parts) < 2:
                return "Usage: get <app_id>"
            return json.dumps(bunny.get_app(parts[1]), indent=2)
        else:
            return f"Unknown Bunny command: {command}. Try: status, apps, regions, deploy, update, get."


class GlobTool:
    """Find files matching a pattern, like Unix find or VS Code glob."""

    description = (
        "Find files matching a glob pattern. Input: glob pattern (e.g., '**/*.py')"
    )

    def execute(self, pattern, path=None) -> str:
        import glob as g
        import os

        base_path = path or os.getcwd()

        # Convert Windows path to proper format
        if isinstance(base_path, str) and len(base_path) == 2 and base_path[1] == ":":
            base_path = base_path + "\\"

        try:
            matches = g.glob(pattern, root_dir=base_path, recursive=True)
            if not matches:
                return f"No files found matching '{pattern}' in {base_path}"
            return "FOUND FILES:\n" + "\n".join(f"- {m}" for m in matches[:50])
        except Exception as e:
            return f"Glob error: {e}"


class GrepTool:
    """Search file contents for a pattern, like Unix grep."""

    description = (
        "Search files for a pattern. Input: search term and optional file pattern"
    )

    def execute(self, pattern, file_pattern="*.py", path=None) -> str:
        import os
        import re

        base_path = path or os.getcwd()
        matches = []
        try:
            for root, dirs, files in os.walk(base_path):
                # Skip hidden and common non-code directories
                dirs[:] = [
                    d
                    for d in dirs
                    if not d.startswith(".")
                    and d not in ("__pycache__", "node_modules", "venv", ".git")
                ]

                for f in files:
                    if not f.endswith((".py", ".js", ".ts", ".txt", ".md", ".json")):
                        continue
                    filepath = os.path.join(root, f)
                    try:
                        with open(
                            filepath, "r", encoding="utf-8", errors="ignore"
                        ) as file:
                            for i, line in enumerate(file, 1):
                                if re.search(pattern, line, re.IGNORECASE):
                                    matches.append(f"{filepath}:{i}: {line.strip()}")
                                    if len(matches) >= 50:
                                        break
                    except:
                        pass
                    if len(matches) >= 50:
                        break
                if len(matches) >= 50:
                    break

            if not matches:
                return f"No matches found for '{pattern}'"
            return "GREP RESULTS:\n" + "\n".join(matches)
        except Exception as e:
            return f"Grep error: {e}"


class ReadFileTool:
    """Read a file's contents."""

    description = "Read a file. Input: file path"

    def execute(self, filepath, max_lines=200) -> str:
        import os

        try:
            if not os.path.exists(filepath):
                return f"File not found: {filepath}"
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = [f.readline() for _ in range(max_lines)]
                content = "".join(lines)
                if len(content) > 10000:
                    content = content[:10000] + "\n... (truncated)"
                return f"FILE: {filepath}\n\n{content}"
        except Exception as e:
            return f"Read error: {e}"


class WriteFileTool:
    """Write content to a file."""

    description = "Write to a file. Input: file path and content"

    def execute(self, filepath, content, append=False) -> str:
        import os

        try:
            mode = "a" if append else "w"
            with open(filepath, mode, encoding="utf-8") as f:
                f.write(content)
            return f"Written to {filepath} ({len(content)} bytes)"
        except Exception as e:
            return f"Write error: {e}"


class ListDirTool:
    """List directory contents."""

    description = "List directory contents. Input: directory path (optional)"

    def execute(self, path=None) -> str:
        import os

        try:
            target = path or os.getcwd()
            if not os.path.exists(target):
                return f"Directory not found: {target}"
            items = []
            for item in os.listdir(target):
                full_path = os.path.join(target, item)
                if os.path.isdir(full_path):
                    items.append(f"{item}/")
                else:
                    size = os.path.getsize(full_path)
                    items.append(f"{item} ({size} bytes)")
            return "DIRECTORY CONTENTS:\n" + "\n".join(items)
        except Exception as e:
            return f"List error: {e}"
