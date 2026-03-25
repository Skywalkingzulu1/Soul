import asyncio
import time
import logging
import os
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VisualRetry")

class TrueVerificationAgent:
    def __init__(self):
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    async def verify_browser_active(self):
        """Confirm the browser is actually the front window."""
        vision = self.eyes.see()
        text = vision.get("text", "").lower()
        # Terminal-specific words we want to NOT see as the primary window
        if "powershell" in text or "directory listing" in text:
            return False, "Still seeing Terminal"
        # Browser-specific UI markers
        if any(k in text for k in ["google", "images", "news", "maps", "shopping"]):
            return True, "Confirmed: Browser UI visible"
        return False, "Uncertain Environment"

    async def main(self):
        print("=" * 60)
        print("  SOUL - NO-HALLUCINATION VISION SEARCH")
        print("=" * 60)

        query = "Latest trends in Azanian digital art"
        
        for attempt in range(1, 4):
            print(f"\n[Attempt {attempt}/3] Execution...")
            
            # Step 1: Force Focus via Taskbar (Aggressive)
            print("  [Action] Forcing Focus (Alt-Tab)...")
            self.executor.hotkey("alt", "tab")
            time.sleep(3)
            
            # Step 2: Clear Address Bar and Type
            print("  [Action] Securing Address Bar and Typing Query...")
            self.executor.click(600, 65) # Top center
            time.sleep(0.5)
            self.executor.hotkey("ctrl", "a")
            self.executor.press("backspace")
            self.executor.type_text(query, base_interval=0.05)
            self.executor.press("enter")
            
            # Step 3: STRICT VISUAL CONFIRMATION
            print("  [Verify] Analyzing screen for True Browser state...")
            time.sleep(5)
            active, reason = await self.verify_browser_active()
            
            if active:
                print(f"\n  [SUCCESS] {reason}")
                print("  [Action] Final confirmation: Interaction scroll.")
                self.executor.scroll(-1000)
                print("\n" + "=" * 60)
                print("  MISSION COMPLETE - TRUE VISUAL VERIFICATION")
                print("=" * 60)
                return
            else:
                print(f"  [REJECTED] {reason}. Results not confirmed.")
                if attempt < 3:
                    print("  [Retry] Attempting focus recovery...")
                    # Try a different focus method: Click the very bottom left (Start area) then browser
                    self.executor.click(20, 1180)
                    time.sleep(1)
                    self.executor.click(200, 1180) # Click taskbar area
                else:
                    print("\n[FAIL] Could not verify browser focus after 3 attempts.")

if __name__ == "__main__":
    agent = TrueVerificationAgent()
    asyncio.run(agent.main())
