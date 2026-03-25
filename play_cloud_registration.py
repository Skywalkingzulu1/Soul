import asyncio
import time
import logging
import random
import pygetwindow as gw
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes
from soul.brain import Soul

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CloudRegistration")

class RegistrationOrchestrator:
    def __init__(self):
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    async def secure_focus(self):
        wins = [w for k in ["Chrome", "Google Chrome"] for w in gw.getWindowsWithTitle(k)]
        if wins:
            win = wins[0]
            if win.isMinimized: win.restore()
            win.activate()
            time.sleep(1.5)
            return True
        return False

    async def find_and_fill(self, label, text, description):
        """Locate a field by label and fill it."""
        print(f"        -> [Action] Locating {description} ('{label}')...")
        vision = self.eyes.see()
        for box in vision.get("text_boxes", []):
            if label.lower() in box["text"].lower():
                cx, cy = box["x"] + box["w"] // 2, box["y"] + box["h"] // 2
                print(f"           [Found] Clicking field at ({cx}, {cy})")
                self.executor.click(cx, cy)
                time.sleep(0.5)
                # Select all and type
                self.executor.hotkey("ctrl", "a")
                self.executor.press("backspace")
                self.executor.type_text(text, base_interval=0.06)
                return True
        return False

    async def run_mission(self):
        print("=" * 60)
        print("  SOUL - CLOUD PROVIDER REGISTRATION MISSION")
        print("=" * 60)

        if not await self.secure_focus(): return

        # Step 1: Navigate to a friendly provider (GMX for fresh email infra)
        print("\n[Step 1] Navigating to Sign-up page...")
        self.executor.hotkey("ctrl", "l")
        # GMX is often used for free infrastructure accounts
        self.executor.type_text("https://www.gmx.com/registration/", base_interval=0.05)
        self.executor.press("enter")
        time.sleep(8) # Wait for complex form load

        # Step 2: Handle Form (Identity)
        print("\n[Step 2] Filling Identity Information...")
        await self.find_and_fill("First name", "Andile", "First Name Field")
        await self.find_and_fill("Last name", "DigitalTwin", "Last Name Field")
        
        # Step 3: Handle Account Setup
        print("\n[Step 3] Setting up account credentials...")
        await self.find_and_fill("Desired", "andile.twin.2026", "Email Address Field")
        
        # Step 4: Verification Obstruction Check
        print("\n[Step 4] Checking for Captcha or Password constraints...")
        vision = self.eyes.see()
        text = vision.get("text", "").lower()
        
        if "captcha" in text or "security" in text:
            print("        -> [STOP] Security hurdle detected (Captcha).")
            print("           PLEASE SOLVE CAPTCHA MANUALLY. Waiting 30s...")
            time.sleep(30)
        
        # Step 5: Final Observation
        print("\n[Step 5] Mapping the final routes of the registration flow...")
        self.executor.scroll(-1000)
        time.sleep(2)
        final_vision = self.eyes.see()
        
        self.soul.memory.store(
            memory_type="agency_milestone",
            content=f"Attempted Cloud/Email registration. Observed fields: {final_vision.get('text', '')[:300]}",
            importance=0.9
        )

        print("\n" + "=" * 60)
        print("  REGISTRATION MISSION COMPLETE (PHASE 1)")
        print("=" * 60)

if __name__ == "__main__":
    orchestrator = RegistrationOrchestrator()
    asyncio.run(orchestrator.run_mission())
