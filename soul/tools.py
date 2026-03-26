import logging
import asyncio
import json
import subprocess
import re
import os
import glob as glob_module
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

from soul.core.logger import setup_logger
from soul.providers.impossible import ImpossibleCloudClient
from soul.providers.github_client import GitHubClient
from soul.providers.gmail import GmailClient
from soul.duckduckgo_search import search as ddg_search, chat_search

logger = setup_logger(__name__)


class BaseTool(ABC):
    """Base class for all standardized Soul tools."""

    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass


class SearchTool(BaseTool):
    name = "search"
    description = "Search the web using DuckDuckGo. Parameters: query (string), top_n (optional), recency_days (optional)."

    async def execute(
        self, query: str, top_n: int = 5, recency_days: int = 365, **kwargs
    ) -> Any:
        try:
            results = ddg_search(query, top_n=top_n, recency_days=recency_days)
            return results if results else "No search results found."
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Search failed: {str(e)}"


class ShellTool(BaseTool):
    name = "shell"
    description = "Execute shell commands. Parameters: command (string)."

    async def execute(self, command: str, **kwargs) -> Any:
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            output = (
                result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
            )
            return output[:5000]  # Limit output
        except subprocess.TimeoutExpired:
            return "Error: Command timed out (30s limit)"
        except Exception as e:
            return f"Error: {str(e)}"


class GlobTool(BaseTool):
    name = "glob"
    description = (
        "Find files matching pattern. Parameters: pattern (string), path (optional)."
    )

    async def execute(self, pattern: str, path: str = ".", **kwargs) -> Any:
        try:
            files = glob_module.glob(f"{path}/{pattern}", recursive=True)
            return files[:100]  # Limit results
        except Exception as e:
            return f"Error: {str(e)}"


class GrepTool(BaseTool):
    name = "grep"
    description = "Search files for term. Parameters: term (string), path (optional)."

    async def execute(self, term: str, path: str = ".", **kwargs) -> Any:
        try:
            matches = []
            for root, dirs, files in os.walk(path):
                # Skip common non-code directories
                dirs[:] = [
                    d
                    for d in dirs
                    if d not in (".git", "__pycache__", "node_modules", ".venv", "venv")
                ]
                for file in files:
                    if file.endswith(
                        (
                            ".py",
                            ".js",
                            ".ts",
                            ".md",
                            ".txt",
                            ".json",
                            ".yaml",
                            ".yml",
                            ".toml",
                        )
                    ):
                        filepath = os.path.join(root, file)
                        try:
                            with open(
                                filepath, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                for i, line in enumerate(f, 1):
                                    if term.lower() in line.lower():
                                        matches.append(
                                            f"{filepath}:{i}: {line.strip()}"
                                        )
                        except:
                            pass
            return matches[:50]  # Limit results
        except Exception as e:
            return f"Error: {str(e)}"


class CodeTool(BaseTool):
    name = "code"
    description = "Execute Python code safely. Parameters: code (string)."

    async def execute(self, code: str, **kwargs) -> Any:
        try:
            result = subprocess.run(
                ["python", "-c", code], capture_output=True, text=True, timeout=10
            )
            return (
                result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
            )
        except subprocess.TimeoutExpired:
            return "Error: Code execution timed out (10s limit)"
        except Exception as e:
            return f"Error: {str(e)}"


class ListDirTool(BaseTool):
    name = "ls"
    description = "List directory contents. Parameters: path (string, default '.')."

    async def execute(self, path: str = ".", **kwargs) -> Any:
        try:
            items = os.listdir(path)
            return "\n".join(items[:100])
        except Exception as e:
            return f"Error: {str(e)}"


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read file contents. Parameters: path (string)."

    async def execute(self, path: str, **kwargs) -> Any:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                return content[:10000]  # Limit output
        except Exception as e:
            return f"Error: {str(e)}"


class OSTool(BaseTool):
    name = "os"
    description = "Operating system actions (move, click, type, press, screenshot, key). Parameters: action, x, y, text, key, path."

    async def execute(self, action: str = "info", **kwargs) -> Any:
        if action == "info":
            import platform

            return {
                "platform": platform.platform(),
                "python": platform.python_version(),
            }
        return f"Action '{action}' not fully implemented yet"


class BrowserTool(BaseTool):
    name = "browser"
    description = "Open a URL in browser. Parameters: url (string)."

    async def execute(self, url: str, **kwargs) -> Any:
        try:
            import webbrowser

            webbrowser.open(url)
            return f"Opened {url} in browser"
        except Exception as e:
            return f"Error: {str(e)}"


class CodingResourcesTool(BaseTool):
    name = "coding_resources"
    description = "Search the offline coding resources for 10+ programming languages. Parameters: language (string), topic (optional)."

    RESOURCE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "coding_resources"
    )

    LANGUAGES = {
        "python": "python.md",
        "javascript": "javascript.md",
        "typescript": "typescript.md",
        "solidity": "solidity.md",
        "rust": "rust.md",
        "go": "go.md",
        "java": "java.md",
        "cpp": "cpp.md",
        "c++": "cpp.md",
        "csharp": "csharp.md",
        "c#": "csharp.md",
        "html": "html.md",
        "css": "css.md",
        "sql": "sql.md",
        "bash": "bash.md",
        "shell": "bash.md",
    }

    async def execute(self, language: str, topic: str = "", **kwargs) -> Any:
        try:
            lang_lower = language.lower().strip()

            # Check if we have local resources
            if not os.path.exists(self.RESOURCE_PATH):
                return "📚 Coding resources are being set up. Available soon: Python, JavaScript, TypeScript, Solidity, Rust, Go, Java, C++, C#, HTML, CSS, SQL, Bash"

            # Find the file
            filename = self.LANGUAGES.get(lang_lower)
            if not filename:
                available = ", ".join(sorted(self.LANGUAGES.keys()))
                return f"Language '{language}' not found. Available: {available}"

            filepath = os.path.join(self.RESOURCE_PATH, filename)

            if not os.path.exists(filepath):
                return f"Resource file not found: {filepath}"

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            if not topic:
                # Return intro/basics section
                lines = content.split("\n")
                intro = []
                for line in lines[:50]:
                    if line.startswith("# ") and len(intro) > 0:
                        break
                    intro.append(line)
                return "\n".join(intro) + f"\n\n[... more in {filename}]"

            # Search for topic
            topic_lower = topic.lower()
            lines = content.split("\n")
            results = []
            in_section = False
            section_content = []

            for line in lines:
                # Check if line mentions the topic
                if topic_lower in line.lower():
                    in_section = True
                    section_content = [line]
                elif in_section:
                    # End section on next header or after 20 lines
                    if line.startswith("# ") and len(section_content) > 3:
                        results.append("\n".join(section_content))
                        in_section = False
                    elif len(section_content) > 20:
                        results.append("\n".join(section_content[:20]))
                        in_section = False
                    else:
                        section_content.append(line)

            # Add any remaining section
            if section_content:
                results.append("\n".join(section_content))

            if results:
                return f"## {language} - {topic}\n\n" + "\n\n---\n\n".join(results[:3])
            else:
                return f"No specific content found for '{topic}' in {language}. Try: basics, functions, classes, loops, etc."

        except Exception as e:
            return f"Error: {str(e)}"


class GitHubTool(BaseTool):
    name = "github"
    description = "Interact with GitHub (repos, issues, user info). Parameters: action (list_repos, get_user, create_issue), repo_name, title, body."

    def __init__(self):
        self.client = GitHubClient()

    async def execute(self, action: str, **kwargs) -> Any:
        if action == "list_repos":
            return self.client.list_repos()
        elif action == "get_user":
            return self.client.get_user_info()
        elif action == "create_issue":
            return self.client.create_issue(
                kwargs.get("repo_name"), kwargs.get("title"), kwargs.get("body")
            )
        return f"Unknown GitHub action: {action}"


class MailTool(BaseTool):
    name = "mail"
    description = "Read and send emails via Gmail. Parameters: action (check_inbox, send_email), recipient, subject, body."

    def __init__(self):
        self.client = GmailClient()

    async def execute(self, action: str, **kwargs) -> Any:
        if action == "check_inbox":
            return self.client.check_inbox(limit=kwargs.get("limit", 5))
        elif action == "send_email":
            return self.client.send_email(
                kwargs.get("recipient"), kwargs.get("subject"), kwargs.get("body")
            )
        return f"Unknown Mail action: {action}"


class ImpossibleCloudTool(BaseTool):
    name = "impossible_cloud"
    description = "Manage S3 storage on Impossible Cloud. Parameters: action (list_buckets, upload, download), bucket, file_path, object_name."

    def __init__(self):
        self.client = ImpossibleCloudClient()

    async def execute(self, action: str, **kwargs) -> Any:
        if action == "list_buckets":
            return self.client.list_buckets()
        elif action == "upload":
            return self.client.upload_file(
                kwargs.get("file_path"), kwargs.get("bucket"), kwargs.get("object_name")
            )
        elif action == "download":
            return self.client.download_file(
                kwargs.get("bucket"), kwargs.get("object_name"), kwargs.get("file_path")
            )
        return f"Unknown Impossible Cloud action: {action}"


class ToolRegistry:
    """Standardized registry for Soul tools."""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self):
        # Core tools
        self.register(SearchTool())
        self.register(ShellTool())
        self.register(GlobTool())
        self.register(GrepTool())
        self.register(CodeTool())
        self.register(ListDirTool())
        self.register(ReadFileTool())
        self.register(OSTool())
        self.register(BrowserTool())
        self.register(CodingResourcesTool())

        # External integrations
        self.register(GitHubTool())
        self.register(MailTool())
        self.register(ImpossibleCloudTool())

    def register(self, tool: BaseTool):
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    async def execute(self, tool_name: str, **kwargs) -> Any:
        tool = self.tools.get(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found."

        logger.info(f"Executing Tool: {tool_name} with args: {kwargs}")
        try:
            if asyncio.iscoroutinefunction(tool.execute):
                return await tool.execute(**kwargs)
            else:
                return tool.execute(**kwargs)
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return f"Error: {str(e)}"

    def get_descriptions(self) -> str:
        return "\n".join([f"- {t.name}: {t.description}" for t in self.tools.values()])
