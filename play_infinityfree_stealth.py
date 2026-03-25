import asyncio
import os
import sys
import logging
import json
import random

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from browser.automator import Browser
from soul.flows import handle_obstructions
from soul.forms import analyze_form
from soul.captcha import detect_captcha, wait_for_manual_solve

async def login_infinityfree_stealth():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("InfinityFree_Stealth")
    
    print("=" * 60)
    print("  OPERATION: INFINITYFREE STEALTH LOGIN")
    print("  USER: andilexmchunu@gmail.com")
    print("=" * 60)
    
    # Credentials
    values = {
        "email": "andilexmchunu@gmail.com", 
        "password": "A78512345azania"
    }
    
    # Start with slow_mo to look more human and let UI load
    browser = Browser(headless=False, slow_mo=random.randint(50, 150))
    await browser.start()
    
    login_url = "https://app.infinityfree.net/login"
    session_name = "infinityfree_andile"
    
    try:
        # Step 1: Navigate with random delay
        print(f"\n[1/4] Navigating to {login_url}...")
        await asyncio.sleep(random.uniform(1, 3))
        await browser.goto(login_url)
        await asyncio.sleep(random.uniform(4, 7))
        
        # Step 2: Handle obstructions
        await handle_obstructions(browser._page)
        
        # Step 3: Fill Login Form using HUMAN methods
        print("[2/4] Filling login credentials with human-like movements...")
        
        # Random mouse movements
        await browser._page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        await asyncio.sleep(0.5)

        fields = await analyze_form(browser._page)
        
        # Check if we are already logged in
        content = await browser._page.content()
        if "Dashboard" in content or "Accounts" in content:
            print("  [Success] Already logged in.")
            await browser.save_session(session_name)
            return

        for field in fields:
            purpose = field["purpose"]
            if purpose in values:
                selector = f"input[name='{field['name']}']" if field['name'] else f"#{field['id']}"
                if not field['name'] and not field['id']:
                    # Fallback to more complex selector if needed
                    continue
                
                print(f"  Typing {purpose}...")
                await browser.human_click(selector)
                await browser.human_type(selector, values[purpose])
                await asyncio.sleep(random.uniform(0.5, 1.2))

        # Check for CAPTCHA
        captcha = await detect_captcha(browser._page)
        if captcha["detected"]:
            print("\n[!] CAPTCHA Detected. Please solve it manually in the browser window.")
            # We wait longer for Turnstile/hCaptcha
            solved = await wait_for_manual_solve(browser._page, browser.screenshot, timeout=300)
            if not solved:
                print("  [Error] CAPTCHA solve timed out.")
                return

        # Step 4: Submit with human click
        print("[3/4] Submitting login...")
        submit_selectors = [
            "button[type='submit']",
            "button:has-text('Log In')",
            "button:has-text('Login')",
            "input[type='submit']"
        ]
        
        submitted = False
        for sel in submit_selectors:
            try:
                btn = await browser._page.query_selector(sel)
                if btn and await btn.is_visible():
                    await browser.human_click(sel)
                    submitted = True
                    break
            except Exception: continue
            
        if not submitted:
            await browser._page.keyboard.press("Enter")
            
        print("  Waiting for dashboard redirect...")
        await asyncio.sleep(random.uniform(7, 12))
        await browser.screenshot("infinityfree_stealth_after_login")
        
        # Verify success
        curr_url = browser._page.url
        curr_content = await browser._page.content()
        
        if "dashboard" in curr_url.lower() or "accounts" in curr_url.lower() or "Home" in curr_content:
            print("\n[4/4] Login Successful! Saving session...")
            await browser.save_session(session_name)
            
            # Update knowledge
            creds = {
                "site": "InfinityFree",
                "email": values["email"],
                "password": values["password"],
                "session_name": session_name,
                "status": "logged_in_stealth",
                "timestamp": json.dumps(curr_url)
            }
            with open("knowledge/infinityfree_credentials.json", "w") as f:
                json.dump(creds, f, indent=2)
            print("  [Done] Stealth session and credentials updated.")
        else:
            print("\n[Hurdle] Login might have failed or needs verification.")
            print(f"  Current URL: {curr_url}")
            print("  Check the screenshot 'infinityfree_stealth_after_login' or the browser.")
            await asyncio.sleep(20)

    except Exception as e:
        print(f"\n[ERROR] Stealth login failed: {e}")
        await browser.screenshot("infinityfree_stealth_error")
    finally:
        print("\nBrowser remains open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(login_infinityfree_stealth())
