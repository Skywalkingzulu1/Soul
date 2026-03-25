import logging
import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from soul.core.logger import setup_logger
from soul.providers.impossible import ImpossibleCloudClient
from soul.providers.github_client import GitHubClient
from soul.providers.gmail import GmailClient

logger = setup_logger(__name__)

class BaseTool(ABC):
    """Base class for all standardized Soul tools."""
    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass

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
            return self.client.create_issue(kwargs.get("repo_name"), kwargs.get("title"), kwargs.get("body"))
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
            return self.client.send_email(kwargs.get("recipient"), kwargs.get("subject"), kwargs.get("body"))
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
            return self.client.upload_file(kwargs.get("file_path"), kwargs.get("bucket"), kwargs.get("object_name"))
        elif action == "download":
            return self.client.download_file(kwargs.get("bucket"), kwargs.get("object_name"), kwargs.get("file_path"))
        return f"Unknown Impossible Cloud action: {action}"

class ToolRegistry:
    """Standardized registry for V1.5 Soul tools."""
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(GitHubTool())
        self.register(MailTool())
        self.register(ImpossibleCloudTool())
        # Other tools (Search, Shell, etc.) would be refactored similarly

    def register(self, tool: BaseTool):
        self.tools[tool.name] = tool

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
