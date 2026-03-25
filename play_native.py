import asyncio
import time
import logging
import os
import random
from soul.brain import Soul
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NativeExplorer")

class NativeExplorer:
    def __init__(self):
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    def _human_pause(self, min_s=1.0, max_s=2.0):
        time.sleep(random.uniform(min_s, max_s))

    async def main(self):
        print("=" * 60)
        print("  SOUL - NATIVE CHROME SESSION EXPLORATION")
        print("  Mode: INTERACTING WITH MAIN DESKTOP SESSION")
        print("=" * 60)

        # Step 1: Bringing Main Chrome to Front
        print("\n[Step 1] Bringing main Chrome to focus...")
        self.executor.press("win")
        self._human_pause(0.8, 1.2)
        self.executor.type_text("chrome", base_interval=0.1)
        self._human_pause(1.0, 1.5)
        self.executor.press("enter")
        
        print("  Waiting for window to settle...")
        self._human_pause(3.0, 4.0)

        # Step 2: Visual Mapping of your session
        print("\n[Step 2] Mapping your current session routes...")
        vision = self.eyes.see()
        text_boxes = vision.get("text_boxes", [])
        all_text = vision.get("text", "").lower()
        
        # Look for existing tabs or the address bar
        # Common markers in a native Chrome session
        targets = ["http", "search", "tab", ".com", ".org", "google"]
        
        found_elements = 0
        for target in targets:
            matches = [box for box in text_boxes if target in box["text"].lower()]
            if matches:
                box = matches[0]
                cx, cy = box["x"] + box["w"] // 2, box["y"] + box["h"] // 2
                print(f"  [Found] Route '{target}' detected at ({cx}, {cy})")
                # Visual proof: Move the physical mouse to the detected element
                self.executor.move(cx, cy, duration=1.2)
                self._human_pause(0.5, 1.0)
                found_elements += 1
                if found_elements >= 3: break # Don't hover too many things

        # Step 3: Learning from your current activity
        print("\n[Step 3] Learning from active page content...")
        if all_text:
            summary = vision.get("summary", "User's active session")
            print(f"  [Insight] I see you are currently looking at: {summary[:100]}...")
            
            # Store in long-term memory
            self.soul.memory.store(
                memory_type="native_session_map",
                content=f"Observed user's main Chrome session. Page Content: {all_text[:500]}",
                importance=0.8
            )
            print("  Status: Current session context stored in digital memory.")
        else:
            print("  [Warning] Could not extract text from current session.")

        # Step 4: Spatial Confirmation
        print("\n[Step 4] Confirming spatial reach in native session...")
        # Move to the approximate center of the browser content area
        screen_w, screen_h = self.executor._pyautogui.size()
        self.executor.move(screen_w // 2, screen_h // 2, duration=1.0)
        print("  Action: Centered mouse in content area.")

        print("\n" + "=" * 60)
        print("  NATIVE EXPLORATION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    explorer = NativeExplorer()
    asyncio.run(explorer.main())
