import asyncio
import os
import sys
import logging
import json
import random

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from browser.automator import Browser
from soul.forms import analyze_form, fill_form

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BrowserMail")

startups = [
    {"name": "Flutterwave", "email": "hi@flutterwavego.com"},
    {"name": "Paystack", "email": "hello@paystack.com"},
    {"name": "Moniepoint", "email": "talent@moniepoint.com"},
    {"name": "Chipper Cash", "email": "careers@chippercash.com"},
    {"name": "Yoco", "email": "support@yoco.com"},
    {"name": "Nala", "email": "mamanala@nala.com"},
    {"name": "Kora", "email": "info@korahq.com"},
    {"name": "Honeycoin", "email": "customer.support@honeycoin.app"},
    {"name": "TymeBank", "email": "service@tymebank.co.za"},
    {"name": "Kuda", "email": "help@kuda.com"}
]

GITHUB_REPO = "https://github.com/Skywalkingzulu1"

EMAIL_TEMPLATE = """Dear {name} Team,

I am Andile Sizophila Mchunu (Skywalkingzulu), a Software Developer based in Cape Town with a deep focus on Web3, Decentralized Finance (DeFi), and HealthTech AI. I've been following {name}'s impact on the African financial ecosystem and I'm impressed by your commitment to innovation.

I am reaching out to express my interest in joining your engineering team, specifically in a Senior Backend or Blockchain Solutions role. My recent work at Azania Neptune Labs has involved building self-sovereign infrastructure and high-performance Web3 tools.

You can find my code and projects here: {github}

I build systems that don't depend on anyone else. If the tool doesn't exist, I build it. I am ready to bring this 'build-don't-buy' mindset and my expertise in decentralized infrastructure to {name}.

I'm an action-oriented developer who ships fast and iterates. I'd welcome the opportunity to discuss how I can contribute to your mission.

Directly,
Andile Sizophila Mchunu
Skywalkingzulu
Cape Town, South Africa
"""

async def send_via_gmail(browser, recipient, subject, body):
    page = browser._page
    
    print(f"  Composing to {recipient}...")
    # Click 'Compose'
    try:
        await page.click("div[role='button']:has-text('Compose')")
    except:
        # Try finding by class or text if selector fails
        await page.get_by_role("button", name="Compose").click()
        
    await asyncio.sleep(2)
    
    # Fill Recipient (To)
    await page.type("input[aria-label='To']", recipient)
    await page.keyboard.press("Tab")
    await asyncio.sleep(1)
    
    # Fill Subject
    await page.type("input[name='subjectbox']", subject)
    await page.keyboard.press("Tab")
    await asyncio.sleep(1)
    
    # Fill Body
    # Gmail's body is a contenteditable div
    await page.type("div[aria-label='Message Body']", body)
    await asyncio.sleep(1)
    
    # Click Send
    await page.click("div[role='button']:has-text('Send')")
    await asyncio.sleep(3)
    print(f"  [SUCCESS] Email sent via browser.")

async def run():
    browser = Browser(headless=False, slow_mo=50)
    await browser.start()
    
    try:
        print("[1/2] Navigating to Gmail...")
        await browser.goto("https://mail.google.com")
        await asyncio.sleep(5)
        
        # Check if login is needed
        if "signin" in browser._page.url or "accounts.google.com" in browser._page.url:
            print("  [Action] Login required. Please log in manually or I will try to automate if possible.")
            # For now, we pause for manual login if it hits the sign-in page
            from soul.captcha import wait_for_manual_solve
            print("  Waiting for you to log in to Gmail...")
            # We use this as a 'pause' mechanism
            await wait_for_manual_solve(browser._page, browser.screenshot, timeout=300)
            
        print("[2/2] Starting application batch...")
        for startup in startups:
            subject = f"Engineering Opportunity - Andile Sizophila Mchunu (Senior Backend / Web3)"
            body = EMAIL_TEMPLATE.format(name=startup["name"], github=GITHUB_REPO)
            
            try:
                await send_via_gmail(browser, startup["email"], subject, body)
                await asyncio.sleep(random.uniform(3, 7))
            except Exception as e:
                print(f"  [ERROR] Failed to send to {startup['name']}: {e}")
                await browser.screenshot(f"error_{startup['name']}")
                
    finally:
        print("Closing browser in 10 seconds...")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
