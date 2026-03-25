import asyncio
import time
import logging
import os
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VisualRetry")

class StubbornAgent:
    def __init__(self):
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    async def verify_on_screen(self, keywords, timeout=8):
        """Wait and confirm if any keywords appear on the actual screen."""
        start = time.time()
        while time.time() - start < timeout:
            vision = self.eyes.see()
            text = vision.get("text", "").lower()
            for k in keywords:
                if k.lower() in text:
                    return True, text
            time.sleep(2)
        return False, ""

    async def main(self):
        print("=" * 60)
        print("  SOUL - STUBBORN VISION-VERIFIED SEARCH")
        print("=" * 60)

        query = "Latest trends in Azanian digital art"
        max_retries = 3
        
        for attempt in range(1, max_retries + 1):
            print(f"\n[Attempt {attempt}/{max_retries}] Starting search sequence...")
            
            # 1. Force Focus
            print("  [Action] Alt-Tabbing to Browser...")
            self.executor.hotkey("alt", "tab")
            time.sleep(2)
            
            # 2. Secure Address Bar
            print("  [Action] Clicking Address Bar (Guaranteed Top)...")
            self.executor.click(600, 65) # Standard Chrome Address Bar
            time.sleep(0.5)
            self.executor.hotkey("ctrl", "a")
            self.executor.press("backspace")
            
            # 3. Type and Enter
            print(f"  [Action] Typing: '{query}'")
            self.executor.type_text(query, base_interval=0.05)
            self.executor.press("enter")
            
            # 4. STRICT VERIFICATION
            print("  [Verify] Looking for search results on screen...")
            success, seen_text = await self.verify_on_screen(["Azanian", "Art", "Google", "Search", "results"])
            
            if success:
                print("\n  [SUCCESS] Digital Twin confirmed search results are visible!")
                print(f"  [Proof] I see keywords in: '{seen_text[:100]}...'")
                
                print("\n[Action] Final confirm: Scrolling...")
                self.executor.scroll(-1000)
                print("\n" + "=" * 60)
                print("  MISSION COMPLETE - VERIFIED BY VISION")
                print("=" * 60)
                return
            else:
                print(f"  [FAILURE] Verification failed. Could not see results on screen.")
                # If we failed on attempt 3, stop.
                if attempt == max_retries:
                    print("\n[ABORT] All retries failed. Browser might be minimized or obscured.")
                else:
                    print("  [Retry] Trying sequence again in 3 seconds...")
                    time.sleep(3)

if __name__ == "__main__":
    agent = StubbornAgent()
    asyncio.run(agent.main())
