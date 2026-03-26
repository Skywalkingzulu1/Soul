import asyncio
import os
import logging
from dotenv import load_dotenv
from soul.agentic.outreach import OutreachAgent
from soul.brain import Soul

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestEmail")

async def run_test():
    load_dotenv('C:/Users/molel/Soul/.env')
    
    # Initialize
    soul = Soul()
    outreach = OutreachAgent(soul)
    
    # Test details
    to_email = "andilexmchunu@gmail.com"
    subject = "🛡️ Andile Sentinel: Outreach Test"
    body = """Hi there,

This is a test email from Andile, your Sentinel.

I am checking the outreach system to ensure that my communication channels are air-tight.
I've verified my environment variables and successfully initiated this pulse.

Sentinel Status: S-Tier Ready.

Stay safe,
Andile"""

    print(f"\n📧 Sending test email to {to_email}...")
    success = outreach.send_email(to_email, subject, body)
    
    if success:
        print("\n✅ TEST EMAIL SENT SUCCESSFULLY!")
    else:
        print("\n❌ TEST EMAIL FAILED. Check logs for details.")

if __name__ == "__main__":
    asyncio.run(run_test())
