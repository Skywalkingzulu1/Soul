import asyncio
import time
import logging
import os
import random
from soul.brain import Soul
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ForceSearch")

class ForceAgent:
    def __init__(self):
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    def _human_pause(self, min_s=1.5, max_s=3.0):
        time.sleep(random.uniform(min_s, max_s))

    async def main(self):
        print("=" * 60)
        print("  SOUL - FORCE FOCUS SEARCH MISSION")
        print("=" * 60)

        # 1. Bring Chrome to Front aggressively
        print("\n[Step 1] Bringing Chrome to focus...")
        self.executor.press("win")
        time.sleep(0.5)
        self.executor.type_text("chrome", base_interval=0.08)
        time.sleep(1.0)
        self.executor.press("enter")
        print("  Waiting 5 seconds for full window load...")
        time.sleep(5)

        # 2. Find and CLICK the Address Bar (Crucial for focus)
        print("\n[Step 2] Locating and clicking Address Bar...")
        vision = self.eyes.see()
        addr_pos = None
        # Try to find standard markers like 'https' or 'search'
        for box in vision.get("text_boxes", []):
            if any(k in box["text"].lower() for k in ["https", "search", "google", "type"]):
                addr_pos = (box["x"] + box["w"] // 2, box["y"] + box["h"] // 2)
                print(f"  [Found] Address bar at {addr_pos}. Clicking...")
                self.executor.click(addr_pos[0], addr_pos[1])
                break
        
        if not addr_pos:
            print("  [Note] Address bar text not found. Clicking standard top area...")
            self.executor.click(600, 65) # standard address bar location
        
        time.sleep(1)

        # 3. Perform the search
        query = "Latest trends in Azanian digital art"
        print(f"\n[Step 3] Typing search query: '{query}'")
        # Select all and delete just in case
        self.executor.hotkey("ctrl", "a")
        time.sleep(0.3)
        self.executor.press("backspace")
        time.sleep(0.3)
        
        self.executor.type_text(query, base_interval=0.07)
        time.sleep(0.5)
        self.executor.press("enter")

        # 4. Verification Loop
        print("\n[Step 4] Verifying search results load...")
        for i in range(5):
            time.sleep(3)
            vision = self.eyes.see()
            if "results" in vision.get("text", "").lower() or query.lower() in vision.get("text", "").lower():
                print("  [SUCCESS] Search results detected on screen.")
                break
            print(f"  [Waiting] Results not yet visible (Attempt {i+1}/5)...")

        # 5. Scroll to prove interaction
        print("\n[Step 5] Scrolling results...")
        for _ in range(3):
            self.executor.scroll(-800)
            time.sleep(2)

        print("\n" + "=" * 60)
        print("  FORCE SEARCH MISSION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    agent = ForceAgent()
    asyncio.run(agent.main())
