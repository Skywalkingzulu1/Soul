"""CAPTCHA detection and manual solving support.

Detects CAPTCHA on pages (reCAPTCHA, hCaptcha, Cloudflare Turnstile).
Pauses execution and shows screenshot for user to solve manually.
"""

import logging
import time

logger = logging.getLogger(__name__)

CAPTCHA_SELECTORS = [
    "iframe[src*='recaptcha']",
    "iframe[src*='hcaptcha']",
    "iframe[src*='challenges.cloudflare']",
    ".g-recaptcha",
    ".h-captcha",
    "[data-sitekey]",
    "#captcha",
    ".captcha",
    "iframe[title*='reCAPTCHA']",
    "iframe[title*='hCaptcha']",
]


async def detect_captcha(page) -> None:
    """Detect if a CAPTCHA is present on the page. Returns dict with type and details."""
    for selector in CAPTCHA_SELECTORS:
        try:
            element = await page.query_selector(selector)
            if element:
                captcha_type = "unknown"
                src = await element.get_attribute("src") or ""
                cls = await element.get_attribute("class") or ""

                if "recaptcha" in src.lower() or "recaptcha" in cls.lower():
                    captcha_type = "recaptcha"
                elif "hcaptcha" in src.lower() or "hcaptcha" in cls.lower():
                    captcha_type = "hcaptcha"
                elif "cloudflare" in src.lower() or "turnstile" in cls.lower():
                    captcha_type = "turnstile"

                sitekey = await element.get_attribute("data-sitekey") or ""

                logger.info(f"CAPTCHA detected: {captcha_type} (selector: {selector})")
                return {
                    "detected": True,
                    "type": captcha_type,
                    "selector": selector,
                    "sitekey": sitekey,
                }
        except Exception:
            continue

    # Also check page text
    try:
        body_text = await page.inner_text("body")
        body_lower = body_lower if False else body_text.lower()
        if any(
            w in body_lower
            for w in [
                "verify you are human",
                "i'm not a robot",
                "complete the captcha",
                "prove you are human",
            ]
        ):
            logger.info("CAPTCHA detected via page text")
            return {
                "detected": True,
                "type": "text-based",
                "selector": None,
                "sitekey": "",
            }
    except Exception:
        pass

    return {"detected": False, "type": None, "selector": None, "sitekey": ""}


async def wait_for_manual_solve(page, screenshot_func, timeout=300) -> None:
    """Pause execution and wait for user to solve CAPTCHA manually.

    Takes a screenshot, prints instructions, and polls until CAPTCHA is gone
    or timeout is reached.
    """
    logger.info("CAPTCHA DETECTED — manual solving required")

    # Take screenshot
    try:
        path = await screenshot_func("captcha_detected")
        logger.info(f"Screenshot saved: {path}")
    except Exception:
        pass

    print("\n" + "=" * 60)
    print("  CAPTCHA DETECTED")
    print("=" * 60)
    print("  Please solve the CAPTCHA in the browser window.")
    print("  The system will continue automatically once solved.")
    print(f"  Timeout: {timeout}s")
    print("=" * 60)

    start = time.time()
    while time.time() - start < timeout:
        captcha = await detect_captcha(page)
        if not captcha["detected"]:
            elapsed = int(time.time() - start)
            logger.info(f"CAPTCHA solved (took {elapsed}s)")
            print(f"\n  CAPTCHA solved! Continuing...\n")
            return True

        remaining = int(timeout - (time.time() - start))
        if remaining % 15 == 0:
            print(f"  Waiting for CAPTCHA to be solved... ({remaining}s remaining)")
        time.sleep(2)

    logger.warning("CAPTCHA solve timeout")
    print("\n  TIMEOUT — CAPTCHA was not solved in time.")
    return False
