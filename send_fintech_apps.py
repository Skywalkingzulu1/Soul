import os
import sys
import logging
import json
import asyncio

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Set environment variables for the mail server
os.environ["GMAIL_EMAIL"] = "andilexmchunu@gmail.com"
os.environ["GMAIL_PASSWORD"] = "A78512345azania#"

from soul.mail_server import send_email, get_remaining_sends

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FintechApp")

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

async def run():
    remaining = get_remaining_sends()
    print(f"Remaining sends for today: {remaining}")
    
    if remaining == 0:
        print("Error: Daily send limit reached. Wait for reset.")
        return

    count = 0
    for startup in startups:
        if count >= remaining:
            print(f"Stopping: reached daily limit of 10. Sent {count} emails.")
            break
            
        subject = f"Engineering Opportunity - Andile Sizophila Mchunu (Senior Backend / Web3)"
        body = EMAIL_TEMPLATE.format(name=startup["name"], github=GITHUB_REPO)
        
        print(f"Sending to {startup['name']} ({startup['email']})...")
        try:
            send_email(startup["email"], subject, body_text=body)
            print(f"  [SUCCESS] Email sent.")
            count += 1
            
            # Log to jobs_applied.json
            try:
                with open("knowledge/jobs_applied.json", "r") as f:
                    data = json.load(f)
                
                data["jobs"].append({
                    "title": "Senior Backend / Blockchain",
                    "company": startup["name"],
                    "email": startup["email"],
                    "url": "Direct Email",
                    "applied": True,
                    "applied_at": str(datetime.now())
                })
                
                with open("knowledge/jobs_applied.json", "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"  [Warning] Could not update jobs_applied.json: {e}")
                
            # Brief pause to look human
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"  [ERROR] Failed to send: {e}")

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(run())
