import asyncio
import logging
import os
from dotenv import load_dotenv
from soul.brain import Soul
from soul.agentic.sentinel import Sentinel

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FinalPulse")

async def run_final_pulse():
    load_dotenv('C:/Users/molel/Soul/.env')
    
    # Initialize
    soul = Soul()
    sentinel = Sentinel(soul)
    
    print("\n" + "🚀" * 30)
    print("   ANDILE SENTINEL: FINAL MISSION PULSE")
    print("🚀" * 30 + "\n")
    
    # Run one full pulse cycle in hourly mode
    # This will:
    # 1. Recon (State Sync)
    # 2. Architect (Perfect 3 Repos)
    # 3. Hunter (Bounty Scan)
    # 4. Agent (Job/Outreach)
    # 5. Reporting (Dashboard Update)
    await sentinel.autonomous_cycle(hourly_mode=True)
    
    print("\n" + "✅ " * 30)
    print("   FINAL PULSE COMPLETE: CHECK YOUR DASHBOARD AT http://localhost:8090")
    print("✅ " * 30 + "\n")

if __name__ == "__main__":
    asyncio.run(run_final_pulse())
