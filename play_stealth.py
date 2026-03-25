import time
import logging
import os
import random
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StealthDesktop")

class StealthAutomator:
    def __init__(self):
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def _find_and_click(self, target_texts, description="", timeout=10):
        """Wait for text, find its center, and click it."""
        if isinstance(target_texts, str):
            target_texts = [target_texts]
            
        print(f"  [Stealth] Looking for {target_texts} ({description})...")
        vision = self.eyes.see()
        
        for target in target_texts:
            matches = [box for box in vision.get("text_boxes", []) if target.lower() in box["text"].lower()]
            if matches:
                box = matches[0]
                cx, cy = box["x"] + box["w"] // 2, box["y"] + box["h"] // 2
                print(f"  [Action] Clicking '{target}' at ({cx}, {cy})")
                self.executor.click(cx, cy)
                return True
        return False

    async def run(self):
        print("=" * 60)
        print("  SOUL - STEALTH DESKTOP INTERACTION")
        print("=" * 60)
        
        # 1. State: Identify what's on screen
        print("\n[Phase 1] Analyzing current desktop...")
        vision = self.eyes.see()
        text = vision.get("text", "").lower()
        
        # 2. Logic: What do we do?
        if "twitter" in text or "x.com" in text or "home / x" in text:
            print("  [State] Twitter is already open and visible.")
            if "home" in text or "explore" in text or "notifications" in text:
                print("  [State] Logged in feed detected. Proceeding to scroll...")
                for i in range(5):
                    self.executor.scroll(-1000)
                    time.sleep(random.uniform(2, 4))
                print("\n[SUCCESS] Stealth scroll complete.")
            else:
                print("  [State] Twitter is open but not logged in. Trying to find login fields...")
                if self._find_and_click(["Phone, email", "username"], "Login field"):
                    self.executor.type_text("ever mlaudzi", base_interval=0.1)
                    self.executor.press("enter")
                    print("  [Action] Username entered. Waiting for password field...")
        
        elif "edge" in text or "chrome" in text or "browser" in text or "google" in text:
            print("  [State] Browser found, but not on Twitter. Navigating...")
            # Try to click the address bar (usually top part of screen)
            # We'll look for common browser UI text like "https://" or search box
            if not self._find_and_click(["search or type", "https", "google search"], "Address bar"):
                print("  [Action] Address bar not found via OCR. Trying blind click at top...")
                self.executor.click(500, 60) # Typical address bar location
            
            time.sleep(1)
            self.executor.type_text("https://twitter.com/login", base_interval=0.05)
            self.executor.press("enter")
            print("  [Action] Navigation command sent.")
            
        else:
            print("  [Warning] No active browser or Twitter session detected.")
            print("  [Vision Summary]:", vision.get("summary", "No text found")[:200])
            print("  [Action] Suggesting manual focus on a browser window.")

if __name__ == "__main__":
    import asyncio
    automator = StealthAutomator()
    asyncio.run(automator.run())
