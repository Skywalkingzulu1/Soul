import asyncio
import os
import re
import logging
import time
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from soul.session import save_session, load_session

logger = logging.getLogger(__name__)

class YouTubeTool:
    """Professional YouTube automation tool for the Soul system."""
    description = "Automate YouTube: play videos, search, skip ads, extract info. Input: query or URL string."

    async def execute(self, input_str, duration=120) -> None:
        from youtube_master import YouTubeMaster
        
        master = YouTubeMaster(headless=False)
        await master.start()
        
        try:
            if input_str.startswith("http"):
                await master.play_url(input_str)
            else:
                await master.search(input_str)
                await master.play_first_result()
            
            await asyncio.sleep(5)
            info = await master.get_video_info()
            
            # Initial setup
            await master.set_quality("1080p")
            await master.save_state()
            
            # Monitor and keep playing
            await master.monitor(duration)
            
            return f"Played YouTube: {info.get('title')} ({info.get('channel')})"
        except Exception as e:
            return f"YouTube automation failed: {e}"
        finally:
            await master.close()
