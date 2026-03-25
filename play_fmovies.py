
import asyncio
import time
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

from browser.automator import Browser
from soul.os_automation import OSAutomation

async def play_fmovies_one_piece():
    browser = Browser(headless=False, slow_mo=200) 
    os_tool = OSAutomation()
    
    print("\n" + "="*50)
    print("  SUPER AGENT: FMOVIES SEARCH & PLAY")
    print("="*50)
    
    try:
        await browser.start()
        page = browser._page
        
        # 1. Search Google for fmovies mirrors
        print("[1] Searching Google for working fmovies mirrors...")
        await browser.goto("https://www.google.com/search?q=fmovies+official+mirror+list+2024")
        await asyncio.sleep(4)
        
        # Attempt to bypass potential "Before you continue" Google popup
        try:
            await page.click("button:has-text('Accept all')", timeout=3000)
        except Exception:
            pass
            
        # 2. Extract first promising link (often a mirror list or a direct mirror)
        # We'll try to find common fmovies domains in the search results
        print("[2] Identifying fmovies domain...")
        content = await page.content()
        
        # Common patterns for fmovies
        mirrors = ["fmovies.to", "fmoviesto.cc", "fmovies.name", "fmovies.ps", "fmovies.llc", "fmovies24.to"]
        target_url = None
        
        for m in mirrors:
            if m in content:
                target_url = f"https://{m}"
                print(f"  Found fmovies mirror candidate: {target_url}")
                break
        
        if not target_url:
            # Fallback: Just try a known currently active one
            target_url = "https://fmoviesto.cc"
            print("  No mirror found in Google results, trying default: https://fmoviesto.cc")

        # 3. Navigate to the fmovies site
        print(f"[3] Navigating to {target_url}...")
        await browser.goto(target_url)
        await asyncio.sleep(6)
        
        # 4. Search for One Piece
        print("[4] Searching for One Piece...")
        # Search input is often a standard 'q' or 'keyword'
        search_selectors = ["input[name='keyword']", "input[placeholder*='Search']", "input[type='text']"]
        
        search_found = False
        for sel in search_selectors:
            try:
                if await page.locator(sel).first.is_visible():
                    await page.fill(sel, "One Piece")
                    await page.press(sel, "Enter")
                    search_found = True
                    break
            except Exception:
                continue
        
        if not search_found:
            # Try OS click on center-top and type
            os_tool.execute("click", x=640, y=100)
            os_tool.execute("type", text="One Piece")
            os_tool.execute("press", key="enter")
            
        await asyncio.sleep(5)
        
        # 5. Click the result
        print("[5] Selecting One Piece result...")
        try:
            # Try to find a link with One Piece text
            await page.click("a:has-text('One Piece')", timeout=5000)
        except Exception:
            # Fallback: Click the first image/card
            os_tool.execute("click", x=300, y=400)
            
        await asyncio.sleep(5)
        
        # 6. Click Play
        print("[6] Attempting to start playback...")
        # Many of these sites have an overlay "Play" button
        try:
            await page.click(".btn-play, #play-now, text='Watch Now'", timeout=5000)
        except Exception:
            # Physical click in player area
            os_tool.execute("click", x=640, y=450)
            
        print("\n[SUCCESS] Mission complete. Checking for video...")
        await browser.screenshot("fmovies_final")
        
        print("Enjoy the show! Browser open for 120s.")
        await asyncio.sleep(120)
        
    except Exception as e:
        print(f"\n[ERROR] Super Agent failed: {e}")
        await browser.screenshot("fmovies_error")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(play_fmovies_one_piece())
