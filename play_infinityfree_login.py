import asyncio
import os
import sys
import logging
import json

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from soul.brain import Soul
from browser.automator import Browser
from soul.flows import handle_obstructions
from soul.forms import analyze_form, fill_form, click_next
from soul.captcha import detect_captcha, wait_for_manual_solve

async def login_infinityfree():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("InfinityFree_Login")
    
    print("=" * 60)
    print("  OPERATION: INFINITYFREE LOGIN")
    print("  USER: andilexmchunu@gmail.com")
    print("=" * 60)
    
    # Credentials
    values = {
        "email": "andilexmchunu@gmail.com", 
        "password": "A78512345azania"
    }
    
    browser = Browser(headless=False, slow_mo=100)
    await browser.start()
    
    login_url = "https://app.infinityfree.net/login"
    session_name = "infinityfree_andile"
    
    try:
        # Step 1: Navigate
        print(f"\n[1/4] Navigating to {login_url}...")
        await browser.goto(login_url)
        await asyncio.sleep(5)
        
        # Step 2: Handle obstructions
        await handle_obstructions(browser._page)
        
        # Step 3: Fill Login Form
        print("[2/4] Filling login credentials...")
        fields = await analyze_form(browser._page)
        
        # In case it auto-redirects or we are already logged in
        content = await browser._page.content()
        if "Dashboard" in content or "Accounts" in content:
            print("  [Success] Already logged in.")
            await browser.save_session(session_name)
            return

        if not fields:
            print("  [Error] No login fields found. Checking page state...")
            await browser.screenshot("infinityfree_login_no_fields")
            # Try a quick refresh or direct navigation if stuck
            await browser.goto(login_url)
            await asyncio.sleep(3)
            fields = await analyze_form(browser._page)

        filled = await fill_form(browser._page, fields, values)
        print(f"  [Info] Filled {filled} fields.")
        
        # Check for CAPTCHA
        captcha = await detect_captcha(browser._page)
        if captcha["detected"]:
            print("\n[!] CAPTCHA Detected. Please solve it in the browser.")
            await wait_for_manual_solve(browser._page, browser.screenshot, timeout=300)

        # Step 4: Submit
        print("[3/4] Submitting login...")
        # InfinityFree login button might be named 'Login' or 'Sign In'
        submitted = False
        for text in ["Log In", "Login", "Sign In"]:
            try:
                btn = await browser._page.get_by_role("button", name=text, exact=False).first
                if await btn.is_visible():
                    await btn.click()
                    submitted = True
                    break
            except Exception: continue
            
        if not submitted:
            await browser._page.keyboard.press("Enter")
            
        await asyncio.sleep(8)
        await browser.screenshot("infinityfree_after_login")
        
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
                "status": "logged_in",
                "last_login": json.dumps(curr_url)
            }
            with open("knowledge/infinityfree_credentials.json", "w") as f:
                json.dump(creds, f, indent=2)
            print("  [Done] Session and credentials updated.")
        else:
            print("\n[Hurdle] Login might have failed or needs verification.")
            print(f"  Current URL: {curr_url}")
            print("  Please check the browser window.")
            # Keep open for a bit to allow manual fix
            await asyncio.sleep(30)

    except Exception as e:
        print(f"\n[ERROR] Login failed: {e}")
        await browser.screenshot("infinityfree_login_error")
    finally:
        print("\nClosing browser in 10 seconds...")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(login_infinityfree())
