import asyncio
import time
import logging
import pygetwindow as gw
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes
from soul.brain import Soul

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GMX_Registration")

class GMXOrchestrator:
    def __init__(self):
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()
        self.mission_log = []

    async def secure_focus(self):
        print("  [Action] Securing Browser Focus...")
        wins = [w for k in ["Chrome", "Google Chrome", "GMX", "Registration"] for w in gw.getWindowsWithTitle(k)]
        if wins:
            win = wins[0]
            if win.isMinimized: win.restore()
            win.activate()
            time.sleep(2)
            return True
        print("  [Warning] Browser window not found. Please ensure Chrome is open.")
        return False

    async def perceive_state(self):
        vision = self.eyes.see()
        text = vision.get("text", "").lower()
        boxes = vision.get("text_boxes", [])
        return {"text": text, "boxes": boxes, "summary": vision.get("summary", "")}

    async def handle_consent(self):
        """Check for and dismiss GMX consent/cookie popups."""
        state = await self.perceive_state()
        if "consent" in state["text"] or "agree" in state["text"] or "accept" in state["text"]:
            print("  [Consent] Detected consent page/popup. Attempting to dismiss...")
            for box in state["boxes"]:
                if any(k in box["text"].lower() for k in ["agree", "accept", "ok", "consent"]):
                    print(f"  [Action] Clicking consent button: '{box['text']}' at ({box['x']}, {box['y']})")
                    self.executor.click(box["x"] + box["w"]//2, box["y"] + box["h"]//2)
                    time.sleep(5)
                    return True
            # Fallback: Click center-bottom where 'Accept' often is
            print("  [Action] Fallback: Clicking center-bottom for consent...")
            self.executor.click(960, 850) 
            time.sleep(5)
            return True
        return False

    async def fill_field(self, label_keywords, value, description):
        print(f"\n[Goal] Fill {description}")
        state = await self.perceive_state()
        
        # Strategy 1: OCR-based click
        for box in state["boxes"]:
            if any(k.lower() in box["text"].lower() for k in label_keywords):
                print(f"  [Found] '{box['text']}' at ({box['x']}, {box['y']}). Clicking...")
                # Usually the input is below or to the right of the label, but for many forms, 
                # clicking the label itself focuses the input if properly associated.
                # However, let's try to click slightly to the right or below if it's just a label.
                self.executor.click(box["x"] + box["w"]//2, box["y"] + box["h"] + 20) # Click 20px below
                time.sleep(0.5)
                self.executor.hotkey("ctrl", "a")
                self.executor.press("backspace")
                self.executor.type_text(value, base_interval=0.07)
                time.sleep(2)
                
                # Verify
                new_state = await self.perceive_state()
                if value.lower() in new_state["text"]:
                    print(f"  [Success] {description} filled correctly.")
                    return True
        
        print(f"  [Failure] Could not confidently locate {description}.")
        return False

    async def run_registration(self):
        print("=" * 60)
        print("  SOUL - GMX CLOUD REGISTRATION (ITERATION V3)")
        print("=" * 60)

        if not await self.secure_focus():
            # If not found, try to open it
            import subprocess
            print("  [Action] Opening GMX Registration page...")
            subprocess.Popen(['cmd', '/c', 'start', 'https://www.gmx.com/registration/'])
            time.sleep(10)
            if not await self.secure_focus(): return

        # Handle Consent
        await self.handle_consent()

        # Step 1: First Name
        if not await self.fill_field(["First name", "Firstname"], "Andile", "First Name"):
            # Try a blind tab sequence if OCR failed
            print("  [Retry] Trying Tab sequence for First Name...")
            self.executor.press("tab") 
            self.executor.type_text("Andile", base_interval=0.07)
        
        # Step 2: Last Name
        await self.fill_field(["Last name", "Lastname"], "Mchunu", "Last Name")

        # Step 3: Gender (Usually a radio or select)
        print("\n[Goal] Select Gender")
        state = await self.perceive_state()
        for box in state["boxes"]:
            if "male" in box["text"].lower() and "female" not in box["text"].lower():
                self.executor.click(box["x"] + box["w"]//2, box["y"] + box["h"]//2)
                print("  [Action] Selected Male.")
                break

        print("\n" + "=" * 60)
        print("  ITERATION PAUSED - ANALYSIS REQUIRED")
        print("=" * 60)
        self.eyes.save_screenshot("screenshots/gmx_iteration_v3_state.png")

if __name__ == "__main__":
    orchestrator = GMXOrchestrator()
    asyncio.run(orchestrator.run_registration())
