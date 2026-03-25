import asyncio
import time
import logging
import pygetwindow as gw
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes
from soul.brain import Soul

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartAgentV3")

class SurgicalOrchestrator:
    def __init__(self):
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    async def ensure_single_chrome_focus(self):
        """Find the existing Chrome and bring it to front. No new windows."""
        print("\n[Focus] Locating existing Chrome session...")
        wins = [w for k in ["Chrome", "Google Chrome", "x.com"] for w in gw.getWindowsWithTitle(k)]
        if wins:
            win = wins[0]
            print(f"        -> Reusing window: '{win.title}'")
            if win.isMinimized: win.restore()
            win.activate()
            time.sleep(1.5)
            return True
        print("        -> Error: No Chrome window found to reuse.")
        return False

    async def diagnose_and_fix(self):
        """Use Vision to see what is blocking the mission."""
        vision = self.eyes.see()
        text = vision.get("text", "").lower()
        
        if "powershell" in text or "directory listing" in text:
            print("        -> Diagnosis: Terminal is still in focus. Retrying Alt-Tab...")
            self.executor.hotkey("alt", "tab")
            return True
        
        if any(k in text for k in ["accept", "agree", "cookie", "consent"]):
            print("        -> Diagnosis: Cookie popup detected. Dismissing...")
            # Simple blind click for common cookie button positions if OCR is slow
            self.executor.click(960, 800) 
            return True
            
        return False

    async def execute_surgical_action(self, name, query, verify_keywords):
        print(f"\n[Task] {name}")
        for attempt in range(1, 4):
            print(f"       -> Attempt {attempt}: Navigating existing tab...")
            
            # Use the surgical 'Ctrl+L' navigation route
            self.executor.hotkey("ctrl", "l")
            time.sleep(0.5)
            self.executor.type_text(query, base_interval=0.05)
            self.executor.press("enter")
            
            time.sleep(5) # Wait for load
            
            # Verify and Troubleshoot
            vision = self.eyes.see()
            screen_text = vision.get("text", "").lower()
            
            if any(k.lower() in screen_text for k in verify_keywords):
                print(f"       -> Success: Visual confirmation achieved.")
                return True
            
            print(f"       -> Warning: Verification failed. Diagnosing...")
            if await self.diagnose_and_fix():
                continue # Retry immediately if we found a fix
            time.sleep(2)
            
        return False

    async def run(self):
        print("=" * 60)
        print("  SOUL - SURGICAL AUTONOMOUS MISSION (V3)")
        print("=" * 60)

        if not await self.ensure_single_chrome_focus(): return

        # Stage 1: The Research Task
        query = "South African tech startups to watch 2026"
        await self.execute_surgical_action("Deep Research", query, ["Startups", "South Africa", "2026", "Tech"])

        # Stage 2: The Insight Task (Same Tab)
        print("\n[Task] Refining Insight...")
        query_2 = "What is the most successful fintech in Cape Town?"
        await self.execute_surgical_action("Targeted Drill-down", query_2, ["Fintech", "Cape Town", "Success"])

        print("\n" + "=" * 60)
        print("  SURGICAL MISSION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    agent = SurgicalOrchestrator()
    asyncio.run(agent.run())
