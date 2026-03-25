import asyncio
import time
import logging
import os
import random
from soul.brain import Soul
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SkywalkingZuluSearch")

class SkywalkingZuluAgent:
    def __init__(self):
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    def _human_pause(self, min_s=1.5, max_s=3.0):
        time.sleep(random.uniform(min_s, max_s))

    async def main(self):
        print("=" * 60)
        print("  SOUL - SKYWALKINGZULU PROFILE SEARCH MISSION")
        print("=" * 60)

        # 1. Bring Chrome to Front
        print("\n[Step 1] Bringing Chrome into active focus...")
        self.executor.press("win")
        time.sleep(0.5)
        self.executor.type_text("chrome", base_interval=0.08)
        time.sleep(1.0)
        self.executor.press("enter")
        self._human_pause(3.0, 4.0)

        # 2. Ensure Profile Identity
        print("\n[Step 2] Identifying Skywalkingzulu Profile...")
        vision = self.eyes.see()
        if "skywalkingzulu" in vision.get("text", "").lower() or "skywalking" in vision.get("text", "").lower():
            print("  [Confirmed] Skywalkingzulu profile is active.")
        else:
            print("  [Search] Looking for profile switcher...")
            # If not found, we'll try a common shortcut to open the profile menu
            self.executor.hotkey("ctrl", "shift", "m")
            self._human_pause(1.5, 2.5)
            # Hover over where the name usually is
            self.executor.move(1800, 50) # Top right area

        # 3. Perform Searches
        searches = [
            "Latest trends in Azanian digital art",
            "DeFi ecosystem updates 2026",
            "Global Workspace Theory AI implementation"
        ]

        for i, query in enumerate(searches, 1):
            print(f"\n[Step 3.{i}] Executing Search: '{query}'")
            
            # Use Ctrl+L to focus address bar (Native pro-user route)
            self.executor.hotkey("ctrl", "l")
            self._human_pause(0.5, 1.0)
            
            # Type search query
            self.executor.type_text(query, base_interval=0.06)
            self._human_pause(0.3, 0.7)
            self.executor.press("enter")
            
            # Wait for results and "learn"
            print(f"  [Learning] Processing results for '{query}'...")
            self._human_pause(4.0, 6.0)
            
            # Human-like scrolling to "read"
            for _ in range(2):
                amt = random.randint(-600, -300)
                self.executor.scroll(amt)
                self._human_pause(1.5, 3.0)
            
            # Visual Snapshot
            vision = self.eyes.see()
            summary = vision.get("summary", "Search result page")
            self.soul.memory.store(
                memory_type="search_learning",
                content=f"Skywalkingzulu Search Task: {query}. Observed: {summary[:200]}",
                importance=0.7
            )

        print("\n" + "=" * 60)
        print("  SKYWALKINGZULU SEARCH MISSION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    agent = SkywalkingZuluAgent()
    asyncio.run(agent.main())
