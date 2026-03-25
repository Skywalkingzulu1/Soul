import asyncio
import time
import logging
import os
import pygetwindow as gw
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UltimateFocus")

class UltimateAgent:
    def __init__(self):
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    async def force_chrome_focus(self):
        print("  [Action] Searching for Chrome window in OS...")
        chrome_windows = [w for k in ["Chrome", "Google Chrome", "x.com", "Twitter"] for w in gw.getWindowsWithTitle(k)]
        
        if chrome_windows:
            win = chrome_windows[0]
            print(f"  [Found] Window: '{win.title}'. Forcing to front...")
            try:
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(2)
                return True
            except Exception as e:
                print(f"  [Error] Could not activate window: {e}")
        return False

    async def main(self):
        print("=" * 60)
        print("  SOUL - ULTIMATE WINDOW FOCUS & SEARCH")
        print("=" * 60)

        query = "Latest trends in Azanian digital art"
        
        # 1. Force the OS to give focus to Chrome
        focused = await self.force_chrome_focus()
        if not focused:
            print("  [Warning] Chrome window not found by title. Falling back to Taskbar search...")
            # Click bottom-left area where browser often is
            self.executor.click(200, 1180)
            time.sleep(2)

        # 2. Visual Pre-Verification (Is it the terminal?)
        vision = self.eyes.see()
        text = vision.get("text", "").lower()
        if "powershell" in text or "directory listing" in text:
            print("  [REJECTED] Terminal still in focus. Aborting to prevent mis-typing.")
            return

        # 3. Secure Address Bar and Type
        print(f"  [Action] Focused confirmed. Executing search for: '{query}'")
        self.executor.click(600, 65) # Secure top address bar
        time.sleep(0.5)
        self.executor.hotkey("ctrl", "a")
        self.executor.press("backspace")
        self.executor.type_text(query, base_interval=0.05)
        self.executor.press("enter")

        # 4. Final Visual Verification
        print("  [Verify] Waiting for results...")
        time.sleep(5)
        vision_final = self.eyes.see()
        if query.lower() in vision_final.get("text", "").lower() or "google" in vision_final.get("text", "").lower():
            print("\n  [SUCCESS] Digital Twin has verified the search results in Chrome!")
            self.executor.scroll(-1000)
        else:
            print("\n  [Final Failure] Could not verify search results after typing.")

        print("\n" + "=" * 60)
        print("  MISSION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    agent = UltimateAgent()
    asyncio.run(agent.main())
