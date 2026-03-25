import asyncio
import sys
import logging
from youtube_master import YouTubeMaster

# Minimal logging for background process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def play_forever(query):
    master = YouTubeMaster(headless=False)
    await master.start()
    
    try:
        logger.info(f"Starting Kendrick Lamar mix: {query}")
        await master.search(query)
        await master.play_first_result()
        
        # Initial setup
        await asyncio.sleep(8)
        info = await master.get_video_info()
        logger.info(f"Now Playing: {info.get('title')}")
        
        await master.set_quality("1080p")
        await master.save_state()
        
        # Infinite monitoring loop
        logger.info("Entering infinite playback loop (Ctrl+C to stop in shell if needed)")
        while True:
            await master.skip_ads()
            await master.ensure_playing()
            # Occasionally re-save state or check for video end
            await asyncio.sleep(5)
            
    except Exception as e:
        logger.error(f"Playback error: {e}")
    finally:
        await master.close()

if __name__ == "__main__":
    query = "kendrick lamar mix"
    try:
        asyncio.run(play_forever(query))
    except KeyboardInterrupt:
        logger.info("Playback stopped by user.")
