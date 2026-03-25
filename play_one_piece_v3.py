
import asyncio
import time
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

from browser.automator import Browser
from soul.os_automation import OSAutomation

async def play_one_piece_v3():
    browser = Browser(headless=False, slow_mo=100)
    os_tool = OSAutomation()
    
    print("\n" + "="*50)
    print("  SUPER AGENT: ONE PIECE RECOVERY MISSION")
    print("="*50)
    
    try:
        await browser.start()
        page = browser._page
        context = browser._context
        
        # 1. Direct navigation to the most stable One Piece page on fmovies
        # This skips the search process which is often ad-heavy
        target_url = "https://fmoviesto.cc/anime/watch-one-piece-online-39515"
        print(f"[1] Navigating to: {target_url}")
        await browser.goto(target_url)
        await asyncio.sleep(8)
        
        # Function to close all tabs except the main one (Ad-killer)
        async def kill_popups():
            pages = context.pages
            if len(pages) > 1:
                print(f"  [Ad-Killer] Closing {len(pages)-1} popup(s)...")
                for p in pages[1:]:
                    await p.close()
            return pages[0]

        # 2. Click the 'Watch Now' or 'Play' button
        # This usually triggers the first popup
        print("[2] Triggering video player...")
        await page.mouse.click(640, 450) # Click center of player
        await asyncio.sleep(2)
        page = await kill_popups()
        
        # 3. Handle the "Play" overlay that appears after the first click
        print("[3] Clicking final Play button...")
        # Use physical OS click to ensure we hit it even if there's a transparent div
        os_tool.execute("move", x=640, y=550, duration=0.5) # Typical play button location
        os_tool.execute("click")
        await asyncio.sleep(3)
        page = await kill_popups()

        # 4. Try different servers if it's stuck
        print("[4] Selecting backup server (Vidcloud/UpCloud)...")
        server_selectors = [
            "li[data-type='sub']", 
            ".server-item",
            "text='Vidcloud'",
            "text='UpCloud'"
        ]
        
        for sel in server_selectors:
            try:
                if await page.locator(sel).first.is_visible():
                    print(f"  Switching to server: {sel}")
                    await page.click(sel)
                    await asyncio.sleep(4)
                    page = await kill_popups()
                    break
            except Exception:
                continue

        # 5. Final physical click to start stream
        print("[5] Finalizing playback...")
        os_tool.execute("move", x=640, y=500, duration=0.2)
        os_tool.execute("click")
        
        print("\n[SUCCESS] Check your screen. One Piece should be streaming.")
        await browser.screenshot("one_piece_final_attempt")
        
        print("Super Agent will keep the session alive for 180s.")
        await asyncio.sleep(180)
        
    except Exception as e:
        print(f"\n[ERROR] Super Agent encountered an obstacle: {e}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(play_one_piece_v3())
