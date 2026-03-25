"""Signup flow orchestrator — fully autonomous website registration.

Orchestrates the complete signup process:
1. Create disposable email
2. Navigate to signup page
3. Analyze and fill form fields
4. Handle CAPTCHA (pause for user)
5. Submit form
6. Poll inbox for verification code
7. Enter verification code
8. Save session
9. Return credentials
"""

import asyncio
import json
import os
import time
import random
import string
import logging

from soul.mail import DisposableEmail
from soul.forms import analyze_form, fill_form, click_next
from soul.captcha import detect_captcha, wait_for_manual_solve
from soul.session import save_session, load_session, has_session

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge")


async def handle_obstructions(page) -> None:
    """Detect and click common 'Accept Cookies' or 'Agree' buttons."""
    for text in ["Accept all", "Agree", "I agree", "Allow all", "Accept cookies", "Consent", "OK"]:
        try:
            # Try specific selectors and text content
            btn = await page.query_selector(f"button:has-text('{text}'), a:has-text('{text}')")
            if btn and await btn.is_visible():
                logger.info(f"  [Obstruction] Clicking: {text}")
                await btn.click()
                return True
        except Exception: continue
    
    # Try ID-based for GMX specifically if URL matches
    url = page.url
    if "gmx.com" in url or "signup.gmx.com" in url:
        try:
            # GMX often uses a consent frame or specific ID
            consent_btn = await page.query_selector("#consent_prompt_submit, .consent-button")
            if consent_btn:
                await consent_btn.click()
                return True
        except Exception: pass
        
    return False

async def signup(
    browser,
    site_name,
    signup_url,
    values=None,
    session_name=None,
    captcha_timeout=300,
    email_timeout=120,
) -> None:
    """Complete autonomous signup flow.

    Args:
        browser: Browser instance (automator.py)
        site_name: Human-readable name (e.g., "Twitter", "GitHub")
        signup_url: URL of the signup page
        values: Dict of field values {"first_name": "Andile", "email": "...", ...}
        session_name: Name for saved session (defaults to site_name)
        captcha_timeout: Seconds to wait for manual CAPTCHA solve
        email_timeout: Seconds to wait for verification email

    Returns:
        Dict with credentials and session info
    """
    if not session_name:
        session_name = site_name.lower().replace(" ", "_")

    if not values:
        values = {}

    result = {
        "site": site_name,
        "status": "started",
        "credentials": {},
        "session_path": None,
        "email": None,
        "steps_completed": [],
        "errors": [],
    }

    # Check for existing session
    if has_session(session_name):
        logger.info(f"Existing session found for {site_name}. Skipping signup.")
        result["status"] = "existing_session"
        result["session_path"] = load_session(session_name)
        return result

    disposable = DisposableEmail()

    try:
        # Step 1: Create disposable email
        logger.info(f"[1/8] Creating disposable email for {site_name} signup...")
        email_addr = disposable.create()
        result["email"] = email_addr
        result["steps_completed"].append("email_created")
        logger.info(f"  Disposable email: {email_addr}")

        # If no email in values, use disposable
        if "email" not in values:
            values["email"] = email_addr

        # Step 2: Navigate to signup page
        logger.info(f"[2/8] Navigating to {signup_url}...")
        await browser.goto(signup_url)
        await asyncio.sleep(6) # More time for GMX redirects
        
        # VERIFICATION: Ensure we aren't stuck on a generic landing page or wrong tab
        page = browser._page
        for _ in range(2):
            current_url = page.url.lower()
            content = await page.content()
            
            # If we are on a wrong major domain (like google.com when we want gmx.com)
            target_domain = site_name.lower()
            if target_domain not in current_url and "google.com" in current_url:
                logger.warning(f"  Wrong tab detected ({current_url}). Force navigating to {signup_url}...")
                await page.goto(signup_url, wait_until="networkidle")
                await asyncio.sleep(5)
                continue

            if not any(k in current_url for k in ["signup", "register", "create", "join", "registration", "account"]):
                logger.warning(f"  On landing page ({current_url}). Searching for signup buttons...")
                # Search for buttons with common signup text
                found_link = False
                for text in ["Sign up", "Create account", "Register", "Sign up for free", "Join now"]:
                    try:
                        btn = await page.get_by_role("link", name=text, exact=False).first
                        if await btn.is_visible():
                            logger.info(f"  Clicking found signup link: {text}")
                            await btn.click()
                            await asyncio.sleep(5)
                            found_link = True
                            break
                    except Exception: continue
                if found_link: continue

        await browser.screenshot(f"{session_name}_step2_landing")
        result["steps_completed"].append("navigated")

        # Step 3: Analyze form fields (with iframe support and domain verification)
        logger.info("[3/8] Analyzing form fields...")
        page = browser._page
        
        # DOMAIN VERIFICATION: Are we on the right site?
        target_domain = site_name.lower().split()[0] # e.g. 'gmx' from 'GMX'
        for retry in range(3):
            current_url = page.url.lower()
            if target_domain not in current_url:
                logger.warning(f"  [Hand-Holding] Wrong page detected: {current_url}. Forcing navigation to {signup_url}...")
                await page.goto(signup_url, wait_until="networkidle")
                await asyncio.sleep(5)
            
            # Try to handle GMX-specific consent that might be blocking the form
            await handle_obstructions(page)
            
            # Scroll a bit to trigger lazy loading of form fields
            await page.mouse.wheel(0, 300)
            await asyncio.sleep(2)

            fields = await analyze_form(page)
            if not fields:
                # Check all iframes
                for frame in page.frames[1:]:
                    f_fields = await analyze_form(frame)
                    if f_fields:
                        logger.info(f"  [Found] Form detected in iframe: {frame.url}")
                        fields = f_fields
                        page = frame
                        break
            
            if fields and len(fields) > 2:
                break
            logger.info(f"  [Retry {retry+1}] Searching for more fields (currently found: {len(fields)})")
            await asyncio.sleep(2)

        field_purposes = [f["purpose"] for f in fields]
        logger.info(f"  Found fields: {field_purposes}")
        result["steps_completed"].append("form_analyzed")

        if not fields:
            logger.warning("  STUCK: No form fields detected after 3 retries. Attempting recovery scroll...")
            await page.mouse.wheel(0, 500)
            await asyncio.sleep(2)
            fields = await analyze_form(page)

        # Step 4: Fill form fields with Meta-Reflection
        logger.info("[4/8] Filling form fields with AI Reflection...")
        
        filled_total = 0
        all_purposes_to_fill = set(values.keys())
        filled_purposes = set()
        
        for attempt in range(5): # More attempts for adaptation
            logger.info(f"  --- Reflection Round {attempt + 1} ---")
            
            # 1. Physical Fill
            filled_this_round = await fill_form(page, fields, values)
            filled_total += filled_this_round
            
            # 2. Visual Check: Did we actually fill them?
            await browser.screenshot(f"{session_name}_reflect_{attempt}")
            for f in fields:
                if f["purpose"] in values:
                    try:
                        val = await f["element"].evaluate("el => el.value")
                        if val: filled_purposes.add(f["purpose"])
                    except Exception: pass

            # 3. Decision: Are we done or stuck?
            if all_purposes_to_fill.issubset(filled_purposes):
                logger.info("  [Success] All target fields visually confirmed.")
                break
            
            # 4. Adaptation: Ask the Brain why we are missing fields
            missing = all_purposes_to_fill - filled_purposes
            logger.info(f"  [Missing] {missing}. Analyzing screen for hidden inputs...")
            
            # Use LLM to find the missing fields by description if possible
            content = await page.content()
            from soul.agentic.perceive import analyze_screen
            analysis = analyze_screen(content[:2000], context=f"Missing fields: {missing} during GMX signup")
            logger.info(f"  [AI Analysis] {analysis[:200]}...")

            if "next" in analysis.lower() or "continue" in analysis.lower():
                logger.info("  [AI Hint] Suggested to click 'Next' to reveal more fields.")
                await click_next(page)
                await asyncio.sleep(4)
            else:
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(2)
            
            fields = await analyze_form(page)

        # HAND-HOLDING: Take a screenshot immediately after filling
        await browser.screenshot(f"{session_name}_step4_filled")

        if filled_total == 0 and len(values) > 1:
            logger.error("  STUCK: Form analysis found fields but none were filled. Check selectors.")
            result["errors"].append("Zero fields filled")
            result["status"] = "stuck_on_form"
            return result

        logger.info(f"  [Verification] Hand-holding: {len(filled_purposes)} unique fields filled. Proceeding...")

        result["steps_completed"].append("form_filled")

        # Step 5: Handle CAPTCHA before submit
        logger.info("[5/8] Checking for CAPTCHA...")
        captcha = await detect_captcha(page)
        if captcha["detected"]:
            # Inform user through system state
            state_machine.update(state="ERROR", action="CAPTCHA Detected - Please Solve")
            solved = await wait_for_manual_solve(
                page, browser.screenshot, captcha_timeout
            )
            if not solved:
                result["errors"].append("CAPTCHA not solved in time")
                result["status"] = "captcha_timeout"
                return result
            state_machine.update(state="EXECUTING", action="CAPTCHA Solved - Continuing")
        
        # HAND-HOLDING: If we are still missing critical fields like 'email' or 'password',
        # try one last desperate scroll before submitting.
        if not all_purposes_to_fill.issubset(filled_purposes):
            logger.info("  [Hand-Holding] Still missing fields before submit. Desperate scroll...")
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(3)
            new_fields = await analyze_form(page)
            await fill_form(page, new_fields, values)
            await browser.screenshot(f"{session_name}_step4_final_attempt")
        result["steps_completed"].append("captcha_handled")

        # Step 6: Submit form
        logger.info("[6/8] Submitting form...")
        submitted = await click_next(page)
        if not submitted:
            # Try pressing Enter on last input
            try:
                await page.press("input:last-of-type", "Enter")
                submitted = True
            except Exception:
                pass
        await asyncio.sleep(3)
        await browser.screenshot(f"{session_name}_step6_submitted")
        result["steps_completed"].append("form_submitted")

        # Check for additional CAPTCHA after submit
        captcha2 = await detect_captcha(page)
        if captcha2["detected"]:
            solved = await wait_for_manual_solve(
                page, browser.screenshot, captcha_timeout
            )
            if not solved:
                result["errors"].append("Post-submit CAPTCHA not solved")
            await click_next(page)

        # Step 7: Wait for verification email and enter code
        logger.info("[7/8] Waiting for verification email...")
        message = disposable.wait_for_message(timeout=email_timeout)

        if message:
            code = disposable.extract_verification_code(message)
            link = disposable.extract_verification_link(message)

            if code:
                # Find code input and fill it
                code_filled = False
                for field in fields:
                    if field["purpose"] == "code":
                        try:
                            await field["element"].fill(code)
                            code_filled = True
                            logger.info(f"  Entered code: {code}")
                            break
                        except Exception:
                            continue

                if not code_filled:
                    # Try common selectors
                    for sel in [
                        "input[name*='code']",
                        "input[name*='otp']",
                        "input[name*='token']",
                        "input[name*='pin']",
                        "input[placeholder*='code']",
                        "input[type='number']",
                        "input[maxlength='6']",
                        "input[maxlength='4']",
                    ]:
                        try:
                            await page.fill(sel, code)
                            logger.info(f"  Entered code via {sel}: {code}")
                            code_filled = True
                            break
                        except Exception:
                            continue

                if code_filled:
                    await click_next(page)
                    await asyncio.sleep(3)

            elif link:
                # Navigate to verification link
                await browser.goto(link)
                await asyncio.sleep(3)

            result["steps_completed"].append("verification_complete")
        else:
            logger.warning("  No verification email received")
            result["errors"].append("No verification email")

        await browser.screenshot(f"{session_name}_step7_verified")

        # Step 8: Save session
        logger.info("[8/8] Saving session...")
        if browser._context:
            session_path = await save_session(browser._context, session_name)
            result["session_path"] = session_path
        result["steps_completed"].append("session_saved")

        # Save credentials
        creds = {
            "site": site_name,
            "email": email_addr,
            "email_password": disposable.password,
            "values": values,
            "session_name": session_name,
            "created_at": time.time(),
            "created_at_readable": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
        creds_path = os.path.join(KNOWLEDGE_DIR, f"{session_name}_credentials.json")
        with open(creds_path, "w") as f:
            json.dump(creds, f, indent=2, default=str)

        result["credentials"] = creds
        result["status"] = "success"
        logger.info(f"Signup complete for {site_name}!")
        logger.info(f"  Email: {email_addr}")
        logger.info(f"  Session: {session_name}")
        logger.info(f"  Credentials: {creds_path}")

    except Exception as e:
        logger.error(f"Signup failed: {e}")
        result["errors"].append(str(e))
        result["status"] = "error"
        await browser.screenshot(f"{session_name}_error")

    finally:
        # Don't delete disposable email — user may need it
        pass

    return result


async def login(browser, site_name, login_url, session_name=None) -> None:
    """Resume a saved session or prompt for login.

    Args:
        browser: Browser instance
        site_name: Human-readable name
        login_url: URL of the login page
        session_name: Name of saved session to load

    Returns:
        True if session loaded successfully
    """
    if not session_name:
        session_name = site_name.lower().replace(" ", "_")

    if has_session(session_name):
        logger.info(f"Loading saved session for {site_name}...")
        session_path = load_session(session_name)
        # Browser will use the session's cookies
        await browser.goto(login_url)
        await asyncio.sleep(2)
        logger.info(f"Session loaded: {session_name}")
        return True
    else:
        logger.info(f"No saved session for {site_name}. Navigate to login page.")
        await browser.goto(login_url)
        return False
