import asyncio
import os
import sys
import re
import logging
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTubeAutomator:
    """Master class for stealth-based YouTube automation."""

    def __init__(self, query="lofi hip hop"):
        self.query = query
        self.video_sources = []
        self.ad_patterns = [
            re.compile(pattern) for pattern in [
                r".*doubleclick\.net.*", r".*adservice\.google.*", r".*adnxs\.com.*",
                r".*popads\.net.*", r".*propellerads\.com.*", r".*a-ads\.com.*",
                r".*onclickads\.net.*", r".*ad-delivery\.net.*", r".*vidverto\.io.*"
            ]
        ]

    async def _intercept(self, route):
        if any(p.match(route.request.url) for p in self.ad_patterns):
            # logger.debug(f"Blocking ad request: {route.request.url}")
            return await route.abort()
        await route.continue_()

    def _handle_response(self, response):
        u = response.url
        if "googlevideo.com" in u and (".mp4" in u or ".m4v" in u or ".m4a" in u or "videoplayback" in u):
            if u not in self.video_sources:
                self.video_sources.append(u)
                # logger.info(f"Video source sniffed: {u[:100]}...")

    async def run(self, duration=300):
        """Execute the automation flow."""
        async with async_playwright() as p:
            logger.info("Launching stealth browser...")
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--start-maximized'
                ]
            )
            
            # Using a real-looking user agent
            context = await browser.new_context(
                viewport=None,
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )
            
            page = await context.new_page()
            await Stealth().apply_stealth_async(page)

            # Setup ad-blocking and sniffing
            await page.route("**/*", self._intercept)
            page.on("response", self._handle_response)

            logger.info("Navigating to YouTube...")
            await page.goto("https://www.youtube.com", wait_until="networkidle", timeout=60000)

            # Handle cookie consent popup if it appears
            try:
                # Common YouTube consent buttons (may vary by region)
                consent_selectors = [
                    "button[aria-label='Accept the use of cookies and other data for the purposes described']",
                    "button[aria-label='Agree to the use of cookies and other data for the purposes described']",
                    "tp-yt-paper-button:has-text('Accept all')",
                    "button:has-text('I agree')",
                    "button:has-text('Accept all')"
                ]
                for selector in consent_selectors:
                    if await page.is_visible(selector):
                        logger.info(f"Clicking consent: {selector}")
                        await page.click(selector)
                        await asyncio.sleep(2)
                        break
            except Exception as e:
                logger.warning(f"Cookie consent handling skipped/failed: {e}")

            logger.info(f"Searching for: {self.query}")
            search_input_selectors = ["input#search", "input[name='search_query']", "input.ytd-searchbox"]
            search_found = False
            for selector in search_input_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=15000)
                    await page.type(selector, self.query, delay=100)
                    await page.press(selector, "Enter")
                    search_found = True
                    break
                except Exception:
                    continue
            
            if not search_found:
                screenshot_path = f"screenshots/youtube_error_{int(asyncio.get_event_loop().time())}.png"
                await page.screenshot(path=screenshot_path)
                raise Exception(f"Could not find search input. Screenshot saved to {screenshot_path}")
            
            await page.wait_for_selector("ytd-video-renderer, #video-title", timeout=15000)
            logger.info("Clicking the first video...")
            # Try multiple selectors for the video link
            video_selectors = ["ytd-video-renderer a#video-title", "a#video-title", "h3 a"]
            video_clicked = False
            for selector in video_selectors:
                try:
                    if await page.is_visible(selector):
                        await page.click(selector)
                        video_clicked = True
                        break
                except Exception:
                    continue
            
            if not video_clicked:
                screenshot_path = f"screenshots/youtube_video_error_{int(asyncio.get_event_loop().time())}.png"
                await page.screenshot(path=screenshot_path)
                raise Exception(f"Could not find video to click. Screenshot saved to {screenshot_path}")

            # Monitoring loop
            logger.info(f"Video playback started. Watching for {duration} seconds...")
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < duration:
                # Check for "Skip Ad" button
                try:
                    skip_ad_selector = ".ytp-ad-skip-button, .ytp-skip-ad-button"
                    if await page.is_visible(skip_ad_selector, timeout=1000):
                        logger.info("Skip Ad button detected! Clicking...")
                        await page.click(skip_ad_selector)
                except Exception:
                    pass

                # Check if video is paused (sometimes it needs a kick)
                try:
                    is_playing = await page.evaluate("() => !document.querySelector('video').paused")
                    if not is_playing:
                        # logger.info("Video paused or not started. Clicking play...")
                        await page.click("video", timeout=1000)
                except Exception:
                    pass

                await asyncio.sleep(5)

            logger.info("Automation session finished.")
            await browser.close()

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "lofi hip hop"
    automator = YouTubeAutomator(query=query)
    try:
        asyncio.run(automator.run())
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    except Exception as e:
        logger.error(f"Automation failed: {e}")
