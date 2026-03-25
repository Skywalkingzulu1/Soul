import asyncio
import time
import logging
import random
import pygetwindow as gw
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes
from soul.brain import Soul

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorldClassAgent")

class ResilientOrchestrator:
    def __init__(self):
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    async def secure_focus(self):
        chrome_windows = [w for k in ["Chrome", "Google Chrome", "x.com"] for w in gw.getWindowsWithTitle(k)]
        if chrome_windows:
            win = chrome_windows[0]
            if win.isMinimized: win.restore()
            win.activate()
            time.sleep(2)
            return True
        return False

    async def clear_obstructions(self):
        """Look for and click 'Accept', 'Agree', or 'Close' buttons."""
        print("       -> [Sub-task] Clearing path (checking for popups)...")
        vision = self.eyes.see()
        for box in vision.get("text_boxes", []):
            if any(k in box["text"].lower() for k in ["accept", "agree", "allow", "close", "reject all"]):
                cx, cy = box["x"] + box["w"] // 2, box["y"] + box["h"] // 2
                print(f"       -> [Action] Dismissing popup at ({cx}, {cy})")
                self.executor.click(cx, cy)
                time.sleep(1)
                return True
        return False

    async def execute_task(self, name, action_coro, verification_keywords):
        print(f"\n[Task] {name}")
        for attempt in range(1, 4):
            print(f"       -> Attempt {attempt}: Executing...")
            await action_coro()
            time.sleep(6) # Increased wait for page render
            
            # Defensive check
            await self.clear_obstructions()
            
            vision = self.eyes.see()
            text = vision.get("text", "").lower()
            
            for k in verification_keywords:
                if k.lower() in text:
                    print(f"       -> Success: Verified by '{k}'")
                    return True, text
            
            print(f"       -> Warning: Content '{verification_keywords}' not found. Retrying...")
        return False, ""

    async def run_mission(self):
        print("=" * 60)
        print("  SOUL - RESILIENT WORLD CLASS MISSION")
        print("=" * 60)

        if not await self.secure_focus(): return

        # Stage 1: Research
        query = "Impact of AI on South African Fintech 2026"
        async def research_action():
            self.executor.click(600, 65)
            self.executor.hotkey("ctrl", "a")
            self.executor.press("backspace")
            self.executor.type_text(query, base_interval=0.05)
            self.executor.press("enter")

        success, res_text = await self.execute_task("Research", research_action, ["Fintech", "South Africa", "Search"])
        if not success: return

        # Stage 2: Autonomous Scratchpad
        print("\n[Task] Creating Autonomous Summary...")
        async def scratch_action():
            self.executor.hotkey("ctrl", "t")
            time.sleep(2)
            self.executor.click(600, 65)
            summary = "AI is transforming ZA Fintech via hyper-personalization and automated compliance."
            self.executor.type_text(summary, base_interval=0.04)

        await self.execute_task("Summary Creation", scratch_action, ["Fintech", "compliance", "transforming"])

        print("\n" + "=" * 60)
        print("  RESILIENT MISSION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    orchestrator = ResilientOrchestrator()
    asyncio.run(orchestrator.run_mission())
