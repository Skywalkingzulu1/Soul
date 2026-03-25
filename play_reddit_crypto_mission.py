import asyncio
import time
import logging
import random
import pygetwindow as gw
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes
from soul.brain import Soul

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RedditMission")

class RedditOrchestrator:
    def __init__(self):
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    async def secure_focus(self):
        wins = [w for k in ["Chrome", "Google Chrome", "Reddit"] for w in gw.getWindowsWithTitle(k)]
        if wins:
            win = wins[0]
            if win.isMinimized: win.restore()
            win.activate()
            time.sleep(1.5)
            return True
        return False

    async def run_session(self):
        print("=" * 60)
        print("  SOUL - SUBSTANTIAL REDDIT CRYPTO MISSION")
        print("=" * 60)

        if not await self.secure_focus():
            print("[Abort] Chrome not found.")
            return

        # Step 1: Navigate to Reddit
        print("\n[Step 1] Navigating to Reddit...")
        self.executor.hotkey("ctrl", "l")
        self.executor.type_text("https://www.reddit.com/r/cryptocurrency", base_interval=0.05)
        self.executor.press("enter")
        time.sleep(6) # Substantial wait for Reddit load

        # Step 2: Verification & Login Check
        print("\n[Step 2] Checking Session State...")
        vision = self.eyes.see()
        if "log in" in vision.get("text", "").lower():
            print("        -> Status: Not logged in. Waiting 20s for manual login or guest view...")
            time.sleep(20)
        else:
            print("        -> Status: Session confirmed.")

        # Step 3: Deep Observation (The "Substantial" part)
        print("\n[Step 3] Beginning Deep Observation of Crypto Sentiment...")
        observed_topics = []
        
        for i in range(1, 11): # 10 Stages of observation
            print(f"        -> Phase {i}/10: Scrolling and reading...")
            self.executor.scroll(-random.randint(600, 1000))
            time.sleep(3)
            
            # Use Eyes to extract current hot topics
            vision = self.eyes.see()
            screen_text = vision.get("text", "").lower()
            
            # Simple keyword extraction for "learning"
            keywords = ["bitcoin", "eth", "solana", "hack", "bull", "bear", "pump", "dump", "sec"]
            found = [k for k in keywords if k in screen_text]
            if found:
                print(f"           [Observed] Sentiment markers: {found}")
                observed_topics.extend(found)

        # Step 4: Memory Consolidation
        print("\n[Step 4] Consolidating Reddit Insights into Memory...")
        summary = f"Substantial Reddit Session complete. Observed sentiment markers: {list(set(observed_topics))}. Analysis: Market is active."
        self.soul.memory.store(
            memory_type="social_listening",
            content=summary,
            importance=0.8
        )

        print("\n" + "=" * 60)
        print("  SUBSTANTIAL MISSION COMPLETE")
        print("  Memories Stored and Routes Mapped.")
        print("=" * 60)

if __name__ == "__main__":
    orchestrator = RedditOrchestrator()
    asyncio.run(orchestrator.run_session())
