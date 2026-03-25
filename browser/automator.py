"""Browser automation module — Playwright-based, no AI overhead."""

import asyncio
import logging
import os
import time
import random
from pathlib import Path

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")


class Browser:
    """Playwright browser automation for research, form filling, and signup flows."""

    def __init__(self, headless=False, slow_mo=100):
        self.headless = headless
        self.slow_mo = slow_mo
        self._playwright = None
        self._browser = None
        self._page = None
        self._context = None
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    async def start(self):
        """Launch the browser with stealth plugins."""
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-position=0,0",
                "--ignore-certifcate-errors",
                "--ignore-certifcate-errors-spki-list",
            ],
        )
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            accept_downloads=True,
        )
        self._page = await self._context.new_page()
        
        # Apply stealth to the page
        await Stealth().apply_stealth_async(self._page)
        
        # Override navigator.webdriver
        await self._page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        logger.info(f"Stealth browser started (headless={self.headless})")

    async def human_click(self, selector):
        """Click an element with a natural mouse movement."""
        element = await self._page.wait_for_selector(selector)
        box = await element.bounding_box()
        if box:
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            
            # Move mouse in small steps to simulate human movement
            await self._page.mouse.move(x - 50, y - 50)
            await asyncio.sleep(0.1)
            await self._page.mouse.move(x, y, steps=10)
            await asyncio.sleep(0.2)
            await self._page.mouse.click(x, y)
            await asyncio.sleep(0.5)
        else:
            await self.click(selector)

    async def human_type(self, selector, text, delay=100):
        """Type text with variable delays between keystrokes."""
        await self._page.click(selector)
        for char in text:
            await self._page.keyboard.type(char, delay=delay + random.randint(-20, 50))
            if random.random() < 0.1:  # Occasional pause
                await asyncio.sleep(0.3)
        await asyncio.sleep(0.5)

    async def close(self):
        """Close the browser."""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Browser closed")

    async def goto(self, url, wait_until="domcontentloaded", timeout=30000):
        """Navigate to a URL."""
        if not self._page:
            await self.start()
        logger.info(f"Navigating to: {url}")
        await self._page.goto(url, wait_until=wait_until, timeout=timeout)
        await asyncio.sleep(1)  # Let JS settle

    async def get_title(self):
        return await self._page.title()

    async def get_url(self):
        return self._page.url

    async def get_text(self, selector="body"):
        """Get text content of an element."""
        try:
            element = await self._page.query_selector(selector)
            if element:
                return await element.inner_text()
        except Exception:
            pass
        return ""

    async def get_page_content(self):
        """Get all visible text on the page."""
        try:
            return await self._page.inner_text("body")
        except Exception:
            return ""

    async def screenshot(self, name="screenshot"):
        """Take a screenshot."""
        path = os.path.join(SCREENSHOT_DIR, f"{name}_{int(time.time())}.png")
        await self._page.screenshot(path=path, full_page=False)
        logger.info(f"Screenshot saved: {path}")
        return path

    async def fill(self, selector, value):
        """Fill in an input field."""
        logger.info(f"Filling {selector} with: {value[:20]}...")
        await self._page.fill(selector, value)

    async def type_text(self, selector, text, delay=50):
        """Type text character by character (more human-like)."""
        logger.info(f"Typing into {selector}: {text[:20]}...")
        await self._page.click(selector)
        await self._page.type(selector, text, delay=delay)

    async def click(self, selector):
        """Click an element."""
        logger.info(f"Clicking: {selector}")
        await self._page.click(selector)
        await asyncio.sleep(0.5)

    async def click_text(self, text):
        """Click an element by its visible text."""
        logger.info(f"Clicking text: {text}")
        await self._page.click(f"text={text}")
        await asyncio.sleep(0.5)

    async def press(self, selector, key):
        """Press a key on an element."""
        await self._page.press(selector, key)

    async def wait_for(self, selector, timeout=10000):
        """Wait for an element to appear."""
        logger.info(f"Waiting for: {selector}")
        await self._page.wait_for_selector(selector, timeout=timeout)

    async def wait_for_url(self, url_substring, timeout=30000):
        """Wait for URL to contain a substring."""
        logger.info(f"Waiting for URL containing: {url_substring}")
        start = time.time()
        while time.time() - start < timeout / 1000:
            if url_substring in self._page.url:
                return True
            await asyncio.sleep(0.5)
        return False

    async def select_option(self, selector, value):
        """Select a dropdown option."""
        await self._page.select_option(selector, value)

    async def check(self, selector):
        """Check a checkbox."""
        await self._page.check(selector)

    async def get_options(self, selector):
        """Get available options from a select element."""
        options = await self._page.query_selector_all(f"{selector} option")
        result = []
        for opt in options:
            text = await opt.inner_text()
            value = await opt.get_attribute("value")
            result.append({"text": text.strip(), "value": value})
        return result

    async def find_input(self, label_text):
        """Find an input by its label text. Returns the input selector."""
        # Try label association
        try:
            label = await self._page.query_selector(f"label:has-text('{label_text}')")
            if label:
                for_attr = await label.get_attribute("for")
                if for_attr:
                    return f"#{for_attr}"
        except Exception:
            pass

        # Try placeholder
        try:
            input_el = await self._page.query_selector(
                f"input[placeholder*='{label_text}']"
            )
            if input_el:
                return f"input[placeholder*='{label_text}']"
        except Exception:
            pass

        # Try aria-label
        try:
            input_el = await self._page.query_selector(
                f"input[aria-label*='{label_text}']"
            )
            if input_el:
                return f"input[aria-label*='{label_text}']"
        except Exception:
            pass

        return None

    async def list_inputs(self):
        """List all visible input fields on the page."""
        inputs = await self._page.query_selector_all(
            "input:visible, select:visible, textarea:visible"
        )
        result = []
        for inp in inputs:
            inp_type = await inp.get_attribute("type") or "text"
            name = await inp.get_attribute("name") or ""
            placeholder = await inp.get_attribute("placeholder") or ""
            aria_label = await inp.get_attribute("aria-label") or ""
            result.append(
                {
                    "type": inp_type,
                    "name": name,
                    "placeholder": placeholder,
                    "aria_label": aria_label,
                }
            )
        return result

    async def list_buttons(self):
        """List all visible buttons on the page."""
        buttons = await self._page.query_selector_all(
            "button:visible, input[type='submit']:visible, a[role='button']:visible"
        )
        result = []
        for btn in buttons:
            text = ""
            try:
                text = await btn.inner_text()
            except Exception:
                text = await btn.get_attribute("value") or ""
            result.append({"text": text.strip()[:50]})
        return result

    async def research(self, query):
        """Research a topic using DuckDuckGo."""
        await self.goto("https://duckduckgo.com/")
        await self.fill("input[name='q']", query)
        await self.press("input[name='q']", "Enter")
        await asyncio.sleep(3)

        # Extract results
        results = []
        items = await self._page.query_selector_all("article")
        for item in items[:5]:
            try:
                text = await item.inner_text()
                results.append(text[:200])
            except Exception:
                pass

        if not results:
            try:
                content = await self.get_page_content()
                results = [content[:500]]
            except Exception:
                results = ["No results found"]
        return results

    async def save_session(self, name):
        """Save browser session state."""
        from soul.session import save_session

        if self._context:
            return await save_session(self._context, name)
        return None

    async def load_session(self, name):
        """Start browser with a saved session."""
        from soul.session import load_session

        path = load_session(name)
        if path and self._browser:
            if self._context:
                await self._context.close()
            self._context = await self._browser.new_context(
                viewport={"width": 1280, "height": 900},
                storage_state=path,
            )
            self._page = await self._context.new_page()
            logger.info(f"Session loaded: {name}")
            return True
        return False

    async def detect_captcha(self):
        """Check if CAPTCHA is present on the current page."""
        from soul.captcha import detect_captcha

        if self._page:
            return await detect_captcha(self._page)
        return {"detected": False}

    async def wait_for_captcha_solve(self, timeout=300):
        """Pause until user solves CAPTCHA manually."""
        from soul.captcha import wait_for_manual_solve

        if self._page:
            return await wait_for_manual_solve(self._page, self.screenshot, timeout)
        return False
