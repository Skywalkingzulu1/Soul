
import asyncio
import time
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

from browser.automator import Browser
from soul.os_automation import OSAutomation

async def play_one_piece():
    # Use a persistent context if possible, but for this test a clean one is fine
    browser = Browser(headless=False, slow_mo=200) 
    os_tool = OSAutomation()
    
    print("\n" + "="*50)
    print("  SUPER AGENT: ONE PIECE MISSION (FIXED)")
    print("="*50)
    
    try:
        await browser.start()
        page = browser._page
        
        # 1. Try HiAnime (very popular and currently stable)
        print("[1] Navigating to HiAnime...")
        await browser.goto("https://hianime.to/search?keyword=One+Piece")
        await asyncio.sleep(5)
        
        # 2. Handle potential initial overlays/popups
        print("[2] Clearing potential overlays...")
        try:
            # Click anywhere neutral to clear simple overlays
            await page.mouse.click(10, 10)
            await asyncio.sleep(1)
        except Exception:
            pass

        # 3. Locate the "One Piece" TV Series link
        print("[3] Locating One Piece series...")
        # Common selectors for HiAnime/AniWatch clones
        selectors = [
            "a.dynamic-name[title*='One Piece']",
            "a[title*='One Piece']",
            ".film-detail h3 a",
            ".film-poster-ahref"
        ]
        
        found = False
        for selector in selectors:
            try:
                # Wait briefly for each selector
                element = page.locator(selector).first
                if await element.is_visible():
                    print(f"  Found via selector: {selector}")
                    await element.click()
                    found = True
                    break
            except Exception:
                continue
        
        if not found:
            print("  DOM click failed, attempting OS-level click on first result...")
            # Fallback to physical mouse click on the typical location of the first result
            os_tool.execute("move", x=400, y=500, duration=0.5)
            os_tool.execute("click")
            await asyncio.sleep(3)

        # 4. Navigate to the Watch/Play page
        print("[4] Navigating to playback page...")
        await asyncio.sleep(3)
        
        # Click "Watch Now" button
        try:
            watch_selectors = ["a.btn-play", "text='Watch now'", ".btn-play"]
            for ws in watch_selectors:
                if await page.locator(ws).is_visible():
                    await page.click(ws)
                    print("  Clicked Watch Now button.")
                    break
        except Exception:
            pass
            
        await asyncio.sleep(5)
        
        # 5. Start the Video (Often requires clicking the center of the player)
        print("[5] Starting video stream...")
        # Most players are centered. We'll try to click the center of the viewport.
        await page.mouse.click(640, 360) 
        
        # Fallback OS click for the player "Play" button
        os_tool.execute("move", x=640, y=450, duration=0.5)
        os_tool.execute("click")
        
        print("\n[SUCCESS] One Piece should now be playing.")
        await browser.screenshot("one_piece_fixed_final")
        
        print("Keeping browser open for 120 seconds for you to watch...")
        await asyncio.sleep(120)
        
    except Exception as e:
        print(f"\n[ERROR] Automation failed: {e}")
        await browser.screenshot("one_piece_fixed_error")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(play_one_piece())
