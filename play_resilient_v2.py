import time
import subprocess
import logging
import os
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResilientTwitter")

class TwitterAutomator:
    def __init__(self):
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def _wait_and_verify(self, target_text, timeout=15, description=""):
        """Wait for specific text to appear on screen and return coordinates if found."""
        print(f"  [Verify] Waiting for: '{target_text}' ({description})...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            vision = self.eyes.see()
            matches = [box for box in vision.get("text_boxes", []) if target_text.lower() in box["text"].lower()]
            if matches:
                box = matches[0]
                center_x = box["x"] + box["w"] // 2
                center_y = box["y"] + box["h"] // 2
                print(f"  [Found] '{target_text}' at ({center_x}, {center_y})")
                return center_x, center_y
            
            # Check for common obstructions while waiting
            if "Sign in with Google" in vision.get("text", ""):
                print("  [Obstruction] Detected Google Sign-in popup. Dismissing with ESC...")
                self.executor.press("escape")
                time.sleep(2)
                
            time.sleep(2)
        print(f"  [Timeout] Could not find '{target_text}'")
        return None

    def _see_and_log(self, step_name):
        path = os.path.join(self.screenshot_dir, f"twitter_{step_name}_{int(time.time())}.png")
        self.eyes.save_screenshot(path)
        vision = self.eyes.see()
        summary = vision.get("summary", "No summary")
        print(f"  [Vision] {step_name} state: {summary[:100]}...")
        return vision

    async def run(self, username):
        print("=" * 60)
        print("  SOUL - RESILIENT TWITTER AUTOMATION (V2)")
        print("=" * 60)

        # 1. Open Browser
        print("\n[Step 1] Opening Twitter Login...")
        subprocess.Popen(['cmd', '/c', 'start', 'https://twitter.com/login'])
        
        # 2. Wait for Login Page and Dismiss Obstructions
        login_pos = self._wait_and_verify("Phone, email", timeout=25, description="Username field")
        if not login_pos:
            print("  [Error] Login field hidden or page failed. Retrying dismissal...")
            self.executor.press("escape")
            time.sleep(2)
            login_pos = self._wait_and_verify("Phone, email", timeout=10, description="Username field retry")

        if login_pos:
            self.executor.click(login_pos[0], login_pos[1])
        else:
            print("  [Final Failure] Could not reach username field.")
            self._see_and_log("username_fail")
            return False

        # 3. Enter Username
        print(f"\n[Step 2] Entering Username: {username}...")
        self.executor.type_text(username, base_interval=0.1)
        self.executor.press('enter')
        
        # 4. Verify Password Screen
        pass_pos = self._wait_and_verify("Password", timeout=15, description="Password field")
        if not pass_pos:
            print("  [Error] Failed to reach password screen. Checking for 'incorrect username' error...")
            vision = self._see_and_log("password_screen_fail")
            if "sorry" in vision.get("text", "").lower() or "find" in vision.get("text", "").lower():
                print("  [Insight] Twitter says it cannot find this account.")
            return False
        
        print("\n[Step 3] Password Screen reached.")
        print("  [NOTE] Manual intervention required for password entry.")
        print("  Waiting 15 seconds for user to enter password and click login...")
        time.sleep(15)

        # 5. Verify Successful Login
        print("\n[Step 4] Verifying Final Login State...")
        home_pos = self._wait_and_verify("Home", timeout=20, description="Twitter Feed")
        if home_pos:
            print("\n  [CONFIRMED] Login Successful! Reached Home Feed.")
            self._see_and_log("logged_in_success")
            print("\n[Step 5] Performing Human-like scrolling...")
            for _ in range(3):
                self.executor.scroll(-800)
                time.sleep(3)
            return True
        else:
            print("\n  [Error] Could not confirm login.")
            self._see_and_log("final_verify_fail")
            return False

if __name__ == "__main__":
    import asyncio
    automator = TwitterAutomator()
    asyncio.run(automator.run("ever mlaudzi"))
