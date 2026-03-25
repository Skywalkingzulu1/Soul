import asyncio
import os
import sys
import logging
import json

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from soul.brain import Soul
from browser.automator import Browser
from soul.flows import signup, handle_obstructions

async def train_andile_infinityfree_v2():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("InfinityFree_Training")
    
    print("=" * 60)
    print("  TRAINING ANDILE: INFINITYFREE HOSTING REGISTRATION (V2)")
    print("  CREDENTIALS: andilexmchunu@gmail.com")
    print("=" * 60)
    
    # User provided credentials
    values = {
        "email": "andilexmchunu@gmail.com", 
        "password": "A78512345azania",
        "confirm_password": "A78512345azania",
        "agree": "true" # For Terms of Service
    }
    
    browser = Browser(headless=False, slow_mo=100)
    await browser.start()
    
    signup_url = "https://app.infinityfree.net/register"
    session_name = "infinityfree_andile"
    
    try:
        # We don't use the generic soul.signup because it tries to create a disposable email.
        # Instead, we'll implement a custom flow here or call signup with specific values.
        
        # Step 1: Navigate
        print(f"\n[1/5] Navigating to {signup_url}...")
        await browser.goto(signup_url)
        await asyncio.sleep(5)
        
        # Step 2: Handle potential obstructions (cookies, etc.)
        await handle_obstructions(browser._page)
        
        # Step 3: Fill Form
        from soul.forms import analyze_form, fill_form, click_next
        print("[2/5] Analyzing and filling form...")
        fields = await analyze_form(browser._page)
        
        # Check if we are already logged in or on the wrong page
        if not fields:
            print("  [Warning] No form fields found. Checking if already registered or logged in...")
            content = await browser._page.content()
            if "Dashboard" in content or "Accounts" in content:
                print("  [Success] Already logged in to InfinityFree.")
                await browser.save_session(session_name)
                return
        
        filled = await fill_form(browser._page, fields, values)
        print(f"  [Info] Filled {filled} fields.")
        await browser.screenshot("infinityfree_filled")
        
        # Step 4: Handle CAPTCHA
        from soul.captcha import detect_captcha, wait_for_manual_solve
        captcha = await detect_captcha(browser._page)
        if captcha["detected"]:
            print("\n[!] CAPTCHA Detected. Please solve it in the browser window.")
            solved = await wait_for_manual_solve(browser._page, browser.screenshot, timeout=300)
            if not solved:
                print("  [Error] CAPTCHA solve timed out.")
                return

        # Step 5: Submit
        print("[3/5] Submitting registration form...")
        await click_next(browser._page)
        await asyncio.sleep(5)
        await browser.screenshot("infinityfree_submitted")
        
        # Check for verification requirement
        content = await browser._page.content()
        if "verify your email" in content.lower() or "verification link" in content.lower():
            print("\n[4/5] Verification required. Please check andilexmchunu@gmail.com")
            print("  I will wait up to 5 minutes for you to click the link or for the page to refresh.")
            
            # Wait for user to verify or for the page to transition
            for i in range(30): # 5 minutes total
                await asyncio.sleep(10)
                await browser.screenshot(f"infinityfree_verify_wait_{i}")
                curr_url = browser._page.url
                curr_content = await browser._page.content()
                if "dashboard" in curr_url.lower() or "accounts" in curr_url.lower() or "Create Account" in curr_content:
                    print("  [Success] Verification confirmed!")
                    break
                print(f"  [Waiting] { (i+1)*10 }s passed... Still on verification page.")
        
        # Final Step: Save Session
        print("[5/5] Saving session...")
        await browser.save_session(session_name)
        
        # Store credentials in knowledge
        creds = {
            "site": "InfinityFree",
            "email": values["email"],
            "password": values["password"],
            "session_name": session_name,
            "status": "active"
        }
        with open("knowledge/infinityfree_credentials.json", "w") as f:
            json.dump(creds, f, indent=2)
            
        print("\n[COMPLETE] InfinityFree training session finished.")
        
    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
        await browser.screenshot("infinityfree_failure")
    finally:
        print("\nClosing browser in 10 seconds... (Check the window if needed)")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(train_andile_infinityfree_v2())
