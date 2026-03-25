import asyncio
import time
import os
import sys
import pyautogui
from playwright.async_api import async_playwright

async def resilient_player():
    print("\n" + "="*60)
    print("  SUPER AGENT: 100-ITERATION RESILIENT PLAYER")
    print("="*60)
    
    async with async_playwright() as p:
        # Launch with arguments to reduce bot detection
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized'
            ]
        )
        context = await browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Aggressively close any new tabs that pop up (ad blocker)
        context.on("page", lambda new_page: asyncio.create_task(close_ad_tab(new_page, page)))

        # Target: Episode 1 of One Piece on HiAnime
        target_url = "https://hianime.to/watch/one-piece-100?ep=2142"
        print(f"[*] Navigating to {target_url}...")
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"[!] Navigation warning: {e}")

        print("[*] Page loaded. Starting 100-iteration hammer loop...")
        print("[*] Strategy: Check video status -> Click DOM -> Click OS -> Kill Ads\n")
        
        success = False
        
        for i in range(100):
            print(f"--- Iteration {i+1}/100 ---")
            
            # Check if video is playing anywhere in any frame
            is_playing = await check_video_playing(page)
            if is_playing:
                print("\n>>> SUCCESS: JavaScript confirmed <video> is PLAYING! <<<")
                success = True
                break
                
            # Attempt 1: DOM clicking inside frames
            clicked_dom = await try_dom_clicks(page)
            if clicked_dom:
                print("  [Action] DOM click executed. Waiting to see if it plays...")
                await asyncio.sleep(3)
                continue # loop around to check if it's playing

            # Attempt 2: PyAutoGUI physical click (center of screen)
            print("  [Action] Punching through overlays with physical mouse click...")
            width, height = pyautogui.size()
            # Click slightly above center, usually where the video frame sits
            pyautogui.click(width // 2, int(height * 0.45))
            await asyncio.sleep(2)

        if success:
            print("\n[MISSION ACCOMPLISHED] Enjoy One Piece! Browser will remain open.")
            # Keep open for an hour
            await asyncio.sleep(3600) 
        else:
            print("\n[FAILED] Exhausted 100 iterations. Could not confirm playback.")
            await asyncio.sleep(30)
            
        await browser.close()

async def close_ad_tab(new_page, main_page):
    try:
        await new_page.wait_for_load_state(timeout=5000)
        if new_page != main_page:
            print(f"  [Ad-Killer] Blocked popup tab: {new_page.url}")
            await new_page.close()
    except Exception:
        try:
            await new_page.close()
        except Exception:
            pass

async def check_video_playing(page):
    # Check main page and all iframes dynamically
    for frame in page.frames:
        try:
            # evaluate returns True if a video exists AND is not paused
            playing = await frame.evaluate('''() => {
                const vids = document.querySelectorAll('video');
                for (let v of vids) {
                    // Check if the video is actually playing
                    if (!v.paused && v.currentTime > 0) return true;
                }
                return false;
            }''')
            if playing: return True
        except Exception:
            pass
    return False

async def try_dom_clicks(page):
    # Common classes for video player play buttons
    selectors = [
        '.jw-icon-display', # JWPlayer
        '.vjs-big-play-button', # VideoJS
        '.plyr__control--overlaid', # Plyr
        'button[title="Play"]',
        '.play-button',
        '#start-btn',
        '.bp-btn-play',
        '.play-icon'
    ]
    for frame in page.frames:
        for sel in selectors:
            try:
                # Use a fast timeout for checking
                elem = await frame.query_selector(sel)
                if elem and await elem.is_visible():
                    print(f"  [DOM] Found play button ({sel}) in frame. Clicking...")
                    await elem.click(force=True) # force bypasses invisible divs overlaying the button
                    return True
            except Exception:
                pass
    return False

if __name__ == "__main__":
    asyncio.run(resilient_player())