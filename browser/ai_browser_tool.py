"""AI Browser tool for Soul."""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AIBrowserTool:
    """Tool wrapper for AI-powered browser automation."""

    description = (
        "AI-powered browser automation. Use for complex browser tasks like job applications, "
        "form filling, and research. Input: task description as a string."
    )

    def __init__(self):
        self._browser = None

    async def execute(
        self,
        task: str,
        headless: bool = False,
        model: str = "gpt-oss:120b-cloud",
        max_steps: int = 20,
    ) -> dict:
        """Execute an AI browser task."""
        from browser.ai_browser import AIBrowser

        if self._browser is None:
            self._browser = AIBrowser(headless=headless, model=model)
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


async def apply_to_job(job_url: str, cv_path: Optional[str] = None) -> dict:
    """Apply to a job using AI browser."""
    from browser.ai_browser import AIBrowser

    browser = AIBrowser()
    await browser.start()

    try:
        result = await browser.apply_to_job(job_url, cv_path)
        return result
    finally:
        await browser.close()


async def search_jobs_and_apply(
    job_query: str,
    cv_path: Optional[str] = None,
    num_applications: int = 5,
) -> list:
    """Search for jobs and apply to them automatically."""
    from browser.ai_browser import AIBrowser

    browser = AIBrowser()
    await browser.start()

    try:
        results = await browser.search_and_apply(job_query, cv_path, num_applications)
        return results
    finally:
        await browser.close()
