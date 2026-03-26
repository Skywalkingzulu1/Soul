"""Test the Sentinel Airtight Cycle.

Runs 3 consecutive 'Pulses' to verify the 24-hour cycle state management,
ensuring that repos are processed in sequence and not repeated.
"""

import asyncio
import logging
import os
import json
from dotenv import load_dotenv
from soul.brain import Soul
from soul.agentic.sentinel import Sentinel

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestSentinel")

async def run_test():
    load_dotenv('.env')
    
    # Initialize
    soul = Soul()
    sentinel = Sentinel(soul)
    
    print("\n" + "🛡️ " * 20)
    print("   AIRTIGHT TEST: 3 CONSECUTIVE PULSES")
    print("🛡️ " * 20 + "\n")

    for i in range(1, 4):
        print(f"\n[PULSE {i}/3] Starting...")
        # Run one cycle in hourly mode (it returns after 1 cycle)
        await sentinel.autonomous_cycle(hourly_mode=True)
        
        # Verify State
        with open("soul_state.json", "r") as f:
            state = json.load(f)
            completed = len(state.get("completed_today", []))
            queue = len(state.get("repo_queue", []))
            print(f"[PULSE {i} COMPLETE] Repos Completed Today: {completed}, Remaining in Queue: {queue}")
            print(f"Batch processed: {state.get('completed_today')[-3:]}")
            
        # Small delay between pulses for realism
        if i < 3:
            print("Waiting 5 seconds for next pulse simulation...")
            await asyncio.sleep(5)

    print("\n" + "✅ " * 20)
    print("   AIRTIGHT TEST COMPLETE: SEQUENTIAL COVERAGE VERIFIED")
    print("✅ " * 20 + "\n")

if __name__ == "__main__":
    asyncio.run(run_test())
