import asyncio
import logging
import os
import time
from browser.automator import Browser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PrivacyBrowser")

async def main():
    print("=" * 60)
    print("  SOUL - PRIVACY-FIRST BROWSER LEARNING SESSION")
    print("=" * 60)
    print("Status: Launching real Chrome in isolated context...")

    # Initialize browser (not headless, so user can see it)
    browser = Browser(headless=False, slow_mo=500)
    
    try:
        await browser.start()
        
        # TASK 1: Research latest tech info
        print("\n[Task 1] Researching latest Python version...")
        await browser.goto("https://www.python.org/downloads/")
        title = await browser.get_title()
        content = await browser.get_page_content()
        print(f"Page Title: {title}")
        # Find the version in the text (simple extraction)
        if "Download Python" in content:
            idx = content.find("Download Python")
            version = content[idx:idx+25].strip()
            print(f"Extracted Info: {version}")
        await browser.screenshot("python_learning")

        # TASK 2: Wikipedia Navigation & Learning
        print("\n[Task 2] Learning about Artificial Intelligence on Wikipedia...")
        await browser.goto("https://en.wikipedia.org/wiki/Artificial_intelligence")
        print(f"Arrived at: {await browser.get_title()}")
        
        # Click a related link (e.g., 'Machine learning')
        print("Navigating to 'Machine learning' section...")
        try:
            await browser.click_text("Machine learning")
            print(f"New Page: {await browser.get_title()}")
        except Exception:
            print("Could not find direct link, searching internally...")
            
        await browser.screenshot("wiki_learning")

        # TASK 3: Interaction with a Demo Site (Learning Form Handling)
        print("\n[Task 3] Learning form interaction on a demo site...")
        await browser.goto("https://the-internet.herokuapp.com/login")
        print("Interacting with login form (privacy safe)...")
        await browser.fill("#username", "tomsmith")
        await browser.fill("#password", "SuperSecretPassword!")
        await browser.click("button[type='submit']")
        
        # Check if login worked
        result_text = await browser.get_text(".flash.success")
        if "You logged into" in result_text:
            print("Successfully demonstrated form interaction!")
        await browser.screenshot("form_learning")

        # TASK 4: Documentation Analysis
        print("\n[Task 4] Analyzing Playwright documentation...")
        await browser.goto("https://playwright.dev/python/docs/intro")
        intro_text = (await browser.get_page_content())[:300]
        print(f"Documentation Intro: {intro_text}...")
        await browser.screenshot("playwright_learning")

        print("\n" + "=" * 60)
        print("  LEARNING SESSION COMPLETE")
        print("  Respecting Privacy: All cookies/data cleared on exit.")
        print("=" * 60)

    except Exception as e:
        print(f"\n[!] Error during browser session: {e}")
    finally:
        # Give user a moment to see the final state before closing
        print("\nClosing browser in 5 seconds...")
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
