"""AI-powered browser automation using browser-use with cloud LLMs."""

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Optional

import browser_use
from browser_use import Agent, Browser

# Use local Ollama by default (with fallback to cloud)
os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")


def get_llm(provider: str = "openai", model: Optional[str] = None, **kwargs):
    """Get LLM based on provider."""
    if provider == "openai":
        from browser_use import ChatOpenAI

        model = model or "gpt-4o"
        return ChatOpenAI(model=model)

    elif provider == "anthropic":
        from browser_use import ChatAnthropic

        model = model or "claude-sonnet-4-20250514"
        api_key = kwargs.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
        return ChatAnthropic(model=model, api_key=api_key)

    elif provider == "google":
        from browser_use import ChatGoogle

        model = model or "gemini-2.0-flash"
        api_key = kwargs.get("api_key") or os.environ.get("GOOGLE_API_KEY")
        return ChatGoogle(model=model, api_key=api_key)

    elif provider == "groq":
        from browser_use import ChatGroq

        model = model or "llama-3.3-70b-versatile"
        api_key = kwargs.get("api_key") or os.environ.get("GROQ_API_KEY")
        return ChatGroq(model=model, api_key=api_key)

    elif provider == "ollama":
        from langchain_ollama import ChatOllama

        model = model or "gpt-oss:120b-cloud"
        ollama_base_url = kwargs.get(
            "ollama_base_url", os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        )
        return ChatOllama(model=model, base_url=ollama_base_url)

    else:
        raise ValueError(
            f"Unknown provider: {provider}. Use: openai, anthropic, google, groq, or ollama"
        )


class AIBrowser:
    """AI-powered browser automation using browser-use with cloud LLMs."""

    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None,
        headless: bool = False,
        **llm_kwargs,
    ):
        self.provider = provider
        self.model = model
        self.headless = headless
        self.llm_kwargs = llm_kwargs
        self._agent: Optional[Agent] = None
        self._browser: Optional[Browser] = None
        self._llm = None
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    async def start(self):
        """Initialize the AI browser with the configured LLM."""
        self._llm = get_llm(self.provider, self.model, **self.llm_kwargs)

        self._browser = Browser(headless=self.headless)
        await self._browser.start()

        logger.info(f"AI Browser started with {self.provider}/{self.model}")

    async def execute(self, task: str, max_steps: int = 20) -> dict:
        """Execute an AI task in the browser."""
        if not self._agent:
            await self.start()

        self._agent = Agent(
            task=task,
            llm=self._llm,
            browser=self._browser,
        )

        logger.info(f"Executing task: {task[:100]}...")
        result = await self._agent.run(max_steps=max_steps)

        return {
            "success": result.is_done(),
            "steps": result.steps,
            "final_result": result.final_result,
            "error": result.error if hasattr(result, "error") else None,
        }

    async def goto(self, url: str):
        """Navigate to a URL."""
        if not self._agent:
            await self.start()

        await self._browser.create_new_tab(url)
        logger.info(f"Navigating to: {url}")

    async def screenshot(self, name: str = "screenshot") -> str:
        """Take a screenshot."""
        path = os.path.join(SCREENSHOT_DIR, f"{name}_{int(time.time())}.png")
        await self._browser.take_screenshot(path=path)
        logger.info(f"Screenshot saved: {path}")
        return path

    async def close(self):
        """Close the browser."""
        if self._browser:
            await self._browser.close()
        logger.info("AI Browser closed")

    async def fill_form(self, form_data: dict) -> dict:
        """Fill a form using AI to understand the page structure."""
        if not form_data:
            return {"success": False, "error": "No form data provided"}

        task = f"Fill in the following form fields: {form_data}"
        return await self.execute(task)

    async def apply_to_job(self, job_url: str, cv_path: Optional[str] = None) -> dict:
        """Apply to a job posting using AI."""
        await self.goto(job_url)

        task = "Find and fill out the job application form. Look for fields like name, email, phone, and upload the CV if there's a file upload button. If there's no upload button for CV, note that in your response."

        if cv_path and os.path.exists(cv_path):
            task += f" The CV file is located at: {cv_path}"

        return await self.execute(task, max_steps=30)

    async def search_and_apply(
        self, job_query: str, cv_path: Optional[str] = None, num_applications: int = 5
    ) -> list:
        """Search for jobs and apply to them."""
        await self.goto("https://www.linkedin.com/jobs/search/")

        task = f"Search for '{job_query}' jobs. Click on at least {num_applications} job listings and apply to each one using the Easy Apply button if available. Document which applications were successful."

        result = await self.execute(task, max_steps=50)

        return [result]
