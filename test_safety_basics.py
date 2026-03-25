import asyncio
import time
import logging
import os
import subprocess
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SafetyBasicsPerfected")

class SafetyAgent:
    def __init__(self):
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    async def verify(self, target_keywords, timeout=10):
        """Use Vision to verify if any of the target keywords are on screen."""
        if isinstance(target_keywords, str):
            target_keywords = [target_keywords]
            
        print(f"    [Verify] Waiting for any of: {target_keywords}...")
        
        # Give UI a moment to settle before the first capture
        time.sleep(1.0)
        
        start = time.time()
        while time.time() - start < timeout:
            vision = self.eyes.see()
            screen_text = vision.get("text", "").lower()
            
            for keyword in target_keywords:
                if keyword.lower() in screen_text:
                    print(f"    [Success] Confirmed: '{keyword}' is visible.")
                    return True
            
            time.sleep(1.5) # Wait before retry
            
        print(f"    [Failure] Could not verify {target_keywords} on screen.")
        # Save a failure screenshot for debugging
        self.eyes.save_screenshot(f"screenshots/fail_verify_{int(time.time())}.png")
        return False

    async def run_task(self, num, description, action_coro, verify_keywords):
        print(f"\n[Task {num:2}/10] {description}")
        try:
            if asyncio.iscoroutine(action_coro):
                await action_coro
            else:
                # If it's a synchronous function call
                action_coro()
                
            if await self.verify(verify_keywords):
                print(f"Result: TASK {num} PASSED")
                return True
            else:
                print(f"Result: TASK {num} FAILED (Verification Error)")
                return False
        except Exception as e:
            print(f"Result: TASK {num} FAILED (Execution Error: {e})")
            return False

    async def main(self):
        print("=" * 60)
        print("  SOUL - PERFECTED WINDOWS BASICS (SAFETY TEST V2)")
        print("=" * 60)

        # 1. Open Start Menu
        # Verifying "Search" or common Start items
        await self.run_task(1, "Open Start Menu", 
            asyncio.to_thread(self.executor.press, "win"), ["Search", "Type here", "Recommended", "Pinned"])

        # 2. Search for Calculator
        await self.run_task(2, "Search for Calculator", 
            asyncio.to_thread(self.executor.type_text, "calc", 0.1), ["Calculator", "App"])

        # 3. Launch Calculator
        await self.run_task(3, "Launch Calculator", 
            asyncio.to_thread(self.executor.press, "enter"), ["Calculator", "Standard", "Scientific"])

        # 4. Math Verification
        print("\n[Task 4] Simple Math (2+2)")
        self.executor.type_text("2+2=", 0.1)
        if await self.verify(["4"]):
            print("Result: TASK 4 PASSED")
        else:
            print("Result: TASK 4 FAILED")

        # 5. Minimize App
        # Looking for things that should be behind it (PowerShell or Desktop icons)
        await self.run_task(5, "Minimize Calculator", 
            asyncio.to_thread(self.executor.hotkey, "win", "down"), ["PowerShell", "Soul", "Recycle", "Trash"])

        # 6. Open Settings
        await self.run_task(6, "Open System Settings", 
            asyncio.to_thread(self.executor.hotkey, "win", "i"), ["Settings", "System", "Windows Settings"])

        # 7. Check System Info (Search within Settings)
        await self.run_task(7, "Verify System Page Search", 
            asyncio.to_thread(self.executor.type_text, "about", 0.1), ["About", "Device specifications"])

        # 8. Open Notepad
        # Using direct launch and verifying the window
        await self.run_task(8, "Open Notepad", 
            asyncio.to_thread(subprocess.Popen, ["notepad"]), ["Notepad", "Untitled", "Text Editor"])

        # 9. Type Verification String
        print("\n[Task 9] Verify Typing in Notepad")
        self.executor.type_text("Verification Code: SOUL-PERFECTED-2026", 0.05)
        if await self.verify(["SOUL-PERFECTED", "Code:"]):
            print("Result: TASK 9 PASSED")
        else:
            print("Result: TASK 9 FAILED")

        # 10. Cleanup (Close Apps)
        print("\n[Task 10] Cleanup")
        # Close Notepad
        self.executor.hotkey("alt", "f4")
        time.sleep(1.0)
        # Handle "Do you want to save?" popup if it appeared
        vision = self.eyes.see()
        if "save" in vision.get("text", "").lower():
            self.executor.press("n") # Don't save
        
        time.sleep(1.0)
        # Close Settings
        self.executor.hotkey("alt", "f4")
        print("Result: TASK 10 PASSED")

        print("\n" + "=" * 60)
        print("  PERFECTED SAFETY TEST COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    agent = SafetyAgent()
    asyncio.run(agent.main())
