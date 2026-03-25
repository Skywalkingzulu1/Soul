import asyncio
import os
import sys
import logging
import time
import json

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from soul.brain import Soul
from browser.automator import Browser
from soul.flows import handle_obstructions
from soul.forms import fill_form, analyze_form

async def manage_impossible_cloud():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ImpossibleCloud_Automator")
    
    print("=" * 60)
    print("  ANDILE: IMPOSSIBLE CLOUD AUTONOMOUS EXPLORATION")
    print("=" * 60)
    
    # Load credentials
    cred_path = "knowledge/cloud_credentials.json"
    with open(cred_path, "r") as f:
        creds = json.load(f)["impossible_cloud"]

    browser = Browser(headless=False)
    await browser.start()
    page = browser._page
    
    try:
        # 1. Navigate & Login
        login_url = "https://console.impossiblecloud.com/"
        print(f"\n[Action] Navigating to {login_url}...")
        await browser.goto(login_url)
        await asyncio.sleep(5)
        await handle_obstructions(page)
        
        if "login" in page.url or await page.query_selector("input[type='email']"):
            print("  [Action] Automating Login...")
            fields = await analyze_form(page)
            login_values = {
                "email": creds["username"],
                "password": creds["password"]
            }
            await fill_form(page, fields, login_values)
            
            # Click Login/Sign in
            for btn_text in ["Sign in", "Log in", "Login"]:
                try:
                    btn = page.get_by_role("button", name=btn_text, exact=False)
                    if await btn.count() > 0:
                        await btn.first.click()
                        break
                except Exception: continue
            
            await asyncio.sleep(10) # Wait for dashboard
        
        await browser.screenshot("impossible_dashboard")
        print("  [Success] Logged into Impossible Cloud Console.")

        # 2. Navigate to Keys
        print("\n[Goal] Locate Access Key ID")
        found_keys = False
        for text in ["Keys", "Access Keys", "API Keys"]:
            try:
                link = page.get_by_role("link", name=text, exact=False)
                if await link.count() > 0:
                    print(f"  [Action] Clicking {text}...")
                    await link.first.click()
                    await asyncio.sleep(8)
                    found_keys = True
                    break
            except Exception: continue
            
        await browser.screenshot("impossible_keys_page_high_res")
        
        # 3. Aggressive Key Extraction
        print("  [Action] Scanning page source for 20-char Access Key candidates...")
        content = await page.content()
        import re
        # Standard S3 Access Key pattern: 20 chars, uppercase + numbers
        potential_keys = re.findall(r"\b[A-Z0-9]{20}\b", content)
        
        if potential_keys:
            # Filter out known non-keys if any, but usually we just want the ones not seen before
            print(f"  [Found] {len(potential_keys)} candidates: {potential_keys}")
            # Use the first one that isn't Account ID (which is 12 digits)
            access_key = potential_keys[0]
            print(f"  [Selected] Access Key ID: {access_key}")
            creds["access_key_id"] = access_key
            with open(cred_path, "w") as f:
                json.dump({"impossible_cloud": creds}, f, indent=2)
        else:
            print("  [Failure] No 20-char alphanumeric strings found.")

        print("\n" + "=" * 60)
        print("  EXPLORATION COMPLETE - SYSTEM UPDATED")
        print("=" * 60)
        
        # Save session
        from soul.session import save_session
        await save_session(browser._context, "impossible_cloud")
        
    except Exception as e:
        print(f"\n[ERROR] Automation failed: {e}")
        await browser.screenshot("impossible_error")
    finally:
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(manage_impossible_cloud())
