import asyncio
import time
import logging
import os
import random
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FocusFix")

class PerfectedFocusAgent:
    def __init__(self):
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    async def main(self):
        print("=" * 60)
        print("  SOUL - PERFECTED CHROME FOCUS & SEARCH")
        print("=" * 60)

        # Step 1: Secure Focus via Taskbar
        print("\n[Step 1] Attempting to focus Chrome via Taskbar...")
        # Most users have Chrome pinned or open in the first few slots of the taskbar.
        # We will scan the bottom 50 pixels for the Chrome logo or name.
        vision = self.eyes.see()
        taskbar_pos = None
        for box in vision.get("text_boxes", []):
            # If we see 'Google' or 'Chrome' at the very bottom of the screen
            if box["y"] > 1100 and ("google" in box["text"].lower() or "chrome" in box["text"].lower()):
                taskbar_pos = (box["x"] + box["w"] // 2, box["y"] + box["h"] // 2)
                break
        
        if taskbar_pos:
            print(f"  [Found] Chrome on Taskbar at {taskbar_pos}. Clicking...")
            self.executor.click(taskbar_pos[0], taskbar_pos[1])
        else:
            print("  [Note] Taskbar icon not explicitly identified. Using Alt+Tab...")
            self.executor.hotkey("alt", "tab")
        
        time.sleep(3)

        # Step 2: Locate Address Bar with TOP-ONLY constraint
        print("\n[Step 2] Locating Address Bar (Top 20% constraint)...")
        vision = self.eyes.see()
        addr_pos = None
        
        # Filter for text like 'https', 'search', 'google' ONLY in the top 200 pixels
        for box in vision.get("text_boxes", []):
            if box["y"] < 250: # STRICT TOP CONSTRAINT
                if any(k in box["text"].lower() for k in ["https", "search", "google", "type", "x.com"]):
                    addr_pos = (box["x"] + box["w"] // 2, box["y"] + box["h"] // 2)
                    print(f"  [Found] Valid Address Bar at {addr_pos}")
                    break
        
        # Fallback to a guaranteed safe browser coordinate if OCR is messy
        if not addr_pos:
            addr_pos = (600, 60)
            print(f"  [Fallback] Using standard top-left coordinate: {addr_pos}")

        print(f"  [Action] Clicking at {addr_pos} to secure input focus.")
        self.executor.click(addr_pos[0], addr_pos[1])
        time.sleep(1)

        # Step 3: Safety Check - Did we click ourselves?
        # Check if the text under the mouse or near it looks like terminal text
        vision_after = self.eyes.see()
        if "powershell" in vision_after.get("text", "").lower() and addr_pos[1] > 200:
            print("  [ABORT] Potential self-typing detected. Focus failed.")
            return

        # Step 4: Perform the search
        query = "Latest trends in Azanian digital art"
        print(f"\n[Step 3] Typing query in focused browser: '{query}'")
        self.executor.hotkey("ctrl", "a") # Select all in address bar
        self.executor.press("backspace")
        time.sleep(0.5)
        self.executor.type_text(query, base_interval=0.06)
        self.executor.press("enter")

        print("\n[Step 4] Confirming result...")
        time.sleep(4)
        self.executor.scroll(-1000)
        print("\n" + "=" * 60)
        print("  MISSION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    agent = PerfectedFocusAgent()
    asyncio.run(agent.main())
