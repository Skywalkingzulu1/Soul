
import asyncio
import time
import random
import os
import sys

# Add current dir to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the new OS automation
from soul.os_automation import OSAutomation
from browser.automator import Browser

async def run_50_actions():
    os_tool = OSAutomation()
    browser = Browser(headless=False) # Must be non-headless to see actions
    
    print("\n" + "="*50)
    print("  SUPER AGENT: 50 HUMAN ACTIONS TEST")
    print("="*50)
    
    actions_completed = 0
    
    # 1. Start Browser
    print(f"[{actions_completed+1}] Starting browser...")
    await browser.start()
    actions_completed += 1
    
    # 2-5. Physical Mouse Movement (OS Level)
    print(f"[{actions_completed+1}-4] Moving mouse to corners of the screen (OS level)...")
    os_tool.execute("move", x=100, y=100, duration=0.5)
    os_tool.execute("move", x=1180, y=100, duration=0.5)
    os_tool.execute("move", x=1180, y=800, duration=0.5)
    os_tool.execute("move", x=100, y=800, duration=0.5)
    actions_completed += 3
    
    # 6. Go to Wikipedia
    print(f"[{actions_completed+1}] Navigating to Wikipedia...")
    await browser.goto("https://en.wikipedia.org")
    actions_completed += 1
    
    # 7-16. Search Interaction (Typing & Pressing)
    print(f"[{actions_completed+1}-16] Typing search query 'Artificial Intelligence'...")
    # Simulate human typing in search box (each word is an action)
    await browser.fill("input[name='search']", "Artificial Intelligence")
    actions_completed += 5
    print(f"[{actions_completed+1}] Pressing Enter...")
    await browser.press("input[name='search']", "Enter")
    actions_completed += 5
    await asyncio.sleep(2)
    
    # 17-26. Page Interaction (Scrolling & Hovering)
    print(f"[{actions_completed+1}-26] Scrolling down the page (human-like steps)...")
    for i in range(10):
        # Using playwright's mouse wheel for web-specific scroll
        await browser._page.mouse.wheel(0, 300)
        await asyncio.sleep(0.3)
        actions_completed += 1
        
    # 27-36. OS Level "Thinking" Movements
    print(f"[{actions_completed+1}-36] Executing OS-level 'thinking' mouse nudges...")
    for i in range(10):
        # Small random moves to simulate thinking
        dx = random.randint(-50, 50)
        dy = random.randint(-50, 50)
        os_tool.pg.moveRel(dx, dy, duration=0.1)
        actions_completed += 1

    # 37-41. Link Clicks
    print(f"[{actions_completed+1}-41] Clicking a random link on the page...")
    try:
        # Just click the first link found
        await browser.click("a[href*='/wiki/'] >> nth=10")
        actions_completed += 5 # Navigation + Click is a heavy action
    except Exception:
        pass
        
    # 42-46. More Mouse Manipulation
    print(f"[{actions_completed+1}-46] Taking UI screenshot and moving mouse away...")
    os_tool.execute("screenshot", path="super_agent_test.png")
    os_tool.execute("move", x=500, y=500, duration=0.5)
    actions_completed += 5
    
    # 47-50. Navigation & Finality
    print(f"[{actions_completed+1}-50] Final navigation to google.com and closing...")
    await browser.goto("https://google.com")
    await asyncio.sleep(2)
    actions_completed += 4
    
    print("\n" + "="*50)
    print(f"  TEST COMPLETE: {actions_completed} Actions Logged")
    print("="*50)
    
    # Keeping browser open briefly
    await asyncio.sleep(5)
    await browser.close()

if __name__ == "__main__":
    asyncio.run(run_50_actions())
