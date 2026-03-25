"""AI Browser Tool for Soul brain."""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BrowserTool:
    """AI-powered browser tool using browser-use with 120B Ollama model."""

    description = (
        "AI-powered browser automation. Use for complex tasks like job applications, "
        "form filling, research, and website interaction. Input: natural language task description."
    )

    def __init__(self, provider: str = "ollama", model: Optional[str] = None):
        self.provider = provider
        self.model = model
        self._browser = None

    async def execute(
        self, task: str, headless: bool = False, max_steps: int = 20
    ) -> dict:
        """Execute an AI browser task."""
        from browser.ai_browser import AIBrowser

        if self._browser is None:
            self._browser = AIBrowser(
                provider=self.provider, model=self.model, headless=headless
            )
            await self._browser.start()

        try:
            result = await self._browser.execute(task, max_steps=max_steps)
            return result
        except Exception as e:
            logger.error(f"AI Browser task failed: {e}")
            return {"success": False, "error": str(e)}

    async def close(self):
        """Close the browser."""
        if self._browser:
            await self._browser.close()
            self._browser = None


async def run_browser_task(task: str, headless: bool = False) -> dict:
    """Run a browser task directly."""
    from browser.ai_browser import AIBrowser

    browser = AIBrowser(provider="ollama", headless=headless)
    await browser.start()

    try:
        result = await browser.execute(task)
        return result
    finally:
        await browser.close()
