import asyncio
import os
import sys
import re
import logging
import time
import json
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from soul.session import save_session, load_session, has_session

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTubeMaster:
    """Advanced YouTube automation for research and playback."""

    def __init__(self, session_name="youtube_default", headless=False):
        self.session_name = session_name
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.video_sources = []
        self.ad_patterns = [
            re.compile(pattern) for pattern in [
                r".*doubleclick\.net.*", r".*adservice\.google.*", r".*adnxs\.com.*",
                r".*popads\.net.*", r".*propellerads\.com.*", r".*a-ads\.com.*",
                r".*onclickads\.net.*", r".*ad-delivery\.net.*", r".*vidverto\.io.*"
            ]
        ]

    async def start(self):
        """Initialize browser and page."""
        self.playwright = await async_playwright().start()
        logger.info(f"Launching {'headless ' if self.headless else ''}stealth browser...")
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized'
            ]
        )
        
        # Load session if exists
        storage_state = load_session(self.session_name)
        
        self.context = await self.browser.new_context(
            viewport=None if not self.headless else {"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            storage_state=storage_state
        )
        
        self.page = await self.context.new_page()
        await Stealth().apply_stealth_async(self.page)

        # Ad-blocking and sniffing
        await self.page.route("**/*", self._intercept)
        self.page.on("response", self._handle_response)
        
        # Handle new pages/popups
        self.context.on("page", lambda p: asyncio.create_task(p.close()))

    async def _intercept(self, route):
        if any(p.match(route.request.url) for p in self.ad_patterns):
            return await route.abort()
        await route.continue_()

    def _handle_response(self, response):
        u = response.url
        if "googlevideo.com" in u and ("videoplayback" in u):
            if u not in self.video_sources:
                self.video_sources.append(u)

    async def handle_consent(self):
        """Handle cookie consent if it appears."""
        try:
            consent_selectors = [
                "button[aria-label='Accept the use of cookies and other data for the purposes described']",
                "button[aria-label='Agree to the use of cookies and other data for the purposes described']",
                "tp-yt-paper-button:has-text('Accept all')",
                "button:has-text('I agree')",
                "button:has-text('Accept all')",
                "button:has-text('Reject all')" # Sometimes rejection is faster
            ]
            for selector in consent_selectors:
                if await self.page.is_visible(selector, timeout=2000):
                    logger.info(f"Clicking consent: {selector}")
                    await self.page.click(selector)
                    await asyncio.sleep(2)
                    return True
        except Exception:
            pass
        return False

    async def search(self, query):
        """Search for a query on YouTube."""
        if self.page.url == "about:blank":
            await self.page.goto("https://www.youtube.com", wait_until="networkidle")
            await self.handle_consent()

        logger.info(f"Searching for: {query}")
        search_input_selectors = ["input#search", "input[name='search_query']", "input.ytd-searchbox"]
        
        search_found = False
        for selector in search_input_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)
                await self.page.fill(selector, "") # Clear first
                await self.page.type(selector, query, delay=50)
                await self.page.press(selector, "Enter")
                search_found = True
                break
            except Exception:
                continue
        
        if not search_found:
            # Maybe we are already on a search result page or something is wrong
            # Try to navigate directly
            await self.page.goto(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
            
        await self.page.wait_for_selector("ytd-video-renderer, #video-title", timeout=10000)

    async def play_first_result(self):
        """Click the first video in the search results."""
        logger.info("Clicking the first video...")
        video_selectors = [
            "ytd-video-renderer a#video-title", 
            "a#video-title", 
            "ytd-grid-video-renderer a#video-title",
            "h3 a"
        ]
        
        for selector in video_selectors:
            try:
                if await self.page.is_visible(selector):
                    await self.page.click(selector)
                    return True
            except Exception:
                continue
        return False

    async def play_url(self, url):
        """Go directly to a video URL."""
        logger.info(f"Navigating to video: {url}")
        await self.page.goto(url, wait_until="networkidle")
        await self.handle_consent()

    async def skip_ads(self):
        """Check and click 'Skip Ad' buttons."""
        try:
            skip_selectors = [
                ".ytp-ad-skip-button", 
                ".ytp-skip-ad-button", 
                ".ytp-ad-skip-button-modern",
                "button:has-text('Skip')"
            ]
            for selector in skip_selectors:
                if await self.page.is_visible(selector, timeout=500):
                    logger.info("Skipping ad...")
                    await self.page.click(selector)
                    return True
        except Exception:
            pass
        return False

    async def ensure_playing(self):
        """Ensure the video is playing."""
        try:
            state = await self.page.evaluate("""() => {
                const v = document.querySelector('video');
                if (!v) return 'no_video';
                return v.paused ? 'paused' : 'playing';
            }""")
            
            if state == 'paused':
                logger.info("Video paused, attempting to play...")
                await self.page.click("video", timeout=2000)
            elif state == 'no_video':
                logger.warning("No video element found on page.")
        except Exception:
            pass

    async def set_quality(self, quality="1080p"):
        """Change video quality settings with better robustness."""
        logger.info(f"Attempting to set quality to {quality}")
        try:
            # Open settings
            await self.page.click(".ytp-settings-button", timeout=5000)
            await asyncio.sleep(1)
            
            # Click Quality menu - try multiple ways to find it
            quality_found = False
            menu_items = await self.page.query_selector_all(".ytp-menuitem")
            for item in menu_items:
                text = await item.inner_text()
                if "Quality" in text:
                    await item.click()
                    quality_found = True
                    break
            
            if not quality_found:
                # Try clicking by index or specific class if text fail
                await self.page.click(".ytp-panel-menu .ytp-menuitem:nth-last-child(1)")
                quality_found = True
                
            await asyncio.sleep(1)
            
            # Select desired quality
            options = await self.page.query_selector_all(".ytp-quality-menu .ytp-menuitem")
            best_match = None
            for opt in options:
                text = await opt.inner_text()
                if quality in text:
                    best_match = opt
                    break
            
            if best_match:
                await best_match.click()
                logger.info(f"Quality set to {quality}")
            elif options:
                await options[0].click()
                logger.info("Quality set to highest available")
                
        except Exception as e:
            logger.warning(f"Failed to set quality: {e}")
            # Try to close settings if open by clicking elsewhere or settings button again
            try: await self.page.click(".ytp-settings-button", timeout=2000)
            except Exception: pass

    async def toggle_loop(self):
        """Toggle YouTube's native loop feature."""
        try:
            # Right click on video to open context menu
            await self.page.click("video", button="right")
            await asyncio.sleep(0.5)
            # Click Loop in context menu
            await self.page.click(".ytp-contextmenu .ytp-menuitem:has-text('Loop')")
            logger.info("Toggled loop mode.")
        except Exception as e:
            logger.warning(f"Failed to toggle loop: {e}")

    async def get_comments(self, count=5):
        """Scroll down and extract some comments."""
        try:
            logger.info("Extracting comments...")
            await self.page.evaluate("window.scrollTo(0, 500)")
            await asyncio.sleep(2)
            await self.page.wait_for_selector("ytd-comment-thread-renderer", timeout=10000)
            
            comments = await self.page.evaluate(f"""(count) => {{
                return Array.from(document.querySelectorAll('ytd-comment-thread-renderer'))
                    .slice(0, count)
                    .map(el => ({{
                        author: el.querySelector('#author-text')?.innerText.trim() || '',
                        content: el.querySelector('#content-text')?.innerText.trim() || ''
                    }}));
            }}""", count)
            return comments
        except Exception as e:
            logger.warning(f"Failed to get comments: {e}")
            return []

    async def get_video_info(self):
        """Extract metadata about the current video."""
        try:
            info = await self.page.evaluate("""() => {
                return {
                    title: document.querySelector('h1.ytd-watch-metadata')?.innerText || '',
                    channel: document.querySelector('ytd-channel-name a')?.innerText || '',
                    views: document.querySelector('tp-yt-paper-tooltip#tooltip')?.innerText || '',
                    description: document.querySelector('#description-inline-expander')?.innerText || ''
                }
            }""")
            return info
        except Exception:
            return {}

    async def monitor(self, duration=300):
        """Monitor playback for a certain duration."""
        start_time = time.time()
        while time.time() - start_time < duration:
            await self.skip_ads()
            await self.ensure_playing()
            await asyncio.sleep(5)

    async def save_state(self):
        """Save the current session state."""
        await save_session(self.context, self.session_name)

    async def close(self):
        """Cleanup resources."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

async def main():
    master = YouTubeMaster(headless=False)
    await master.start()
    
    try:
        if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
            await master.play_url(sys.argv[1])
        else:
            query = sys.argv[1] if len(sys.argv) > 1 else "master of puppets"
            await master.search(query)
            await master.play_first_result()
        
        # Give it a second to load
        await asyncio.sleep(5)
        
        info = await master.get_video_info()
        logger.info(f"Playing: {info.get('title')} by {info.get('channel')}")
        
        # Try to set high quality
        await master.set_quality("1080p")
        
        # Save session to remember preferences/cookies
        await master.save_state()
        
        # Monitor for 2 minutes
        await master.monitor(120)
        
    finally:
        await master.close()

if __name__ == "__main__":
    asyncio.run(main())
