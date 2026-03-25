import asyncio
import time
from browser.automator import Browser
from soul.brain import Soul

async def main():
    print("=" * 60)
    print("  SOUL - VISIBLE BROWSER EXPLORATION DEMO")
    print("=" * 60)
    
    # Initialize real browser (not headless) with slow motion
    browser = Browser(headless=False, slow_mo=800)
    soul = Soul(name="Andile")
    
    try:
        print("\n[Step 1] Launching Chrome...")
        await browser.start()
        
        print("[Step 2] Navigating to Wikipedia (World Route 1)...")
        await browser.goto("https://www.wikipedia.org")
        
        print("[Step 3] Identifying Search Route...")
        # Using slow-motion typing so you can see it
        await browser.type_text("input[name='search']", "Space Exploration")
        await browser.press("input[name='search']", "Enter")
        
        print("[Step 4] Reading and Learning from page content...")
        await asyncio.sleep(3)
        title = await browser.get_title()
        print(f"        Success: Reached '{title}'")
        
        # Store what we learned in memory
        soul.memory.store("browser_exploration", f"Explored Wikipedia route for Space Exploration. Page title: {title}")
        
        print("[Step 5] Taking a visual snapshot of the route...")
        path = await browser.screenshot("visible_browser_test")
        print(f"        Snapshot saved to: {path}")
        
        print("\n[Step 6] Exploration complete. Closing in 10 seconds...")
        print("        Feel free to look at the open window.")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"\n[!] Error: {e}")
    finally:
        await browser.close()
        print("\n" + "=" * 60)
        print("  DEMO COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
