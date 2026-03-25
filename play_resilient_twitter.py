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
            # Search for the text in the OCR results
            matches = [box for box in vision.get("text_boxes", []) if target_text.lower() in box["text"].lower()]
            if matches:
                # Return the center of the first match
                box = matches[0]
                center_x = box["x"] + box["w"] // 2
                center_y = box["y"] + box["h"] // 2
                print(f"  [Found] '{target_text}' at ({center_x}, {center_y})")
                return center_x, center_y
            time.sleep(2)
        print(f"  [Timeout] Could not find '{target_text}'")
        return None

    def _see_and_log(self, step_name):
        """Take a screenshot and log what is currently visible."""
        path = os.path.join(self.screenshot_dir, f"twitter_{step_name}_{int(time.time())}.png")
        self.eyes.save_screenshot(path)
        vision = self.eyes.see()
        summary = vision.get("summary", "No summary")
        print(f"  [Vision] {step_name} state: {summary[:100]}...")
        return vision

    async def run(self, username):
        print("=" * 60)
        print("  SOUL - RESILIENT TWITTER AUTOMATION")
        print("=" * 60)

        # 1. Open Browser
        print("\n[Step 1] Opening Twitter Login...")
        subprocess.Popen(['cmd', '/c', 'start', 'https://twitter.com/login'])
        
        # 2. Wait for Login Page
        login_pos = self._wait_and_verify("Phone, email", timeout=20, description="Username field")
        if not login_pos:
            print("  [Error] Login page didn't load or username field not found. Troubleshooting...")
            self._see_and_log("login_fail")
            # Try clicking roughly where the field usually is if OCR missed it
            print("  [Retry] Attempting blind click on username field area...")
            self.executor.click(960, 400) # Common center position
            time.sleep(2)
        else:
            self.executor.click(login_pos[0], login_pos[1])

        # 3. Enter Username
        print(f"\n[Step 2] Entering Username: {username}...")
        self.executor.type_text(username, base_interval=0.1)
        self.executor.press('enter')
        
        # 4. Verify Password Screen
        pass_pos = self._wait_and_verify("Password", timeout=10, description="Password field")
        if not pass_pos:
            print("  [Error] Failed to transition to password screen. Possible bot detection or incorrect username.")
            self._see_and_log("password_screen_fail")
            return False
        
        print("\n[Step 3] Password Screen reached successfully.")
        print("  [NOTE] Manual intervention required for password entry (Security Policy).")
        print("  Waiting 10 seconds for user to enter password and click login...")
        time.sleep(10)

        # 5. Verify Successful Login (Final Confirmation)
        print("\n[Step 4] Verifying Final Login State...")
        # Look for "Home" or "Explore" or "Notifications" which are unique to the logged-in feed
        home_pos = self._wait_and_verify("Home", timeout=15, description="Twitter Feed")
        if home_pos:
            print("\n  [CONFIRMED] Login Successful! Reached Home Feed.")
            self._see_and_log("logged_in_success")
            
            print("\n[Step 5] Performing Human-like scrolling...")
            for i in range(3):
                scroll_amt = -1 * (400 + (i * 200))
                print(f"  Scrolling {scroll_amt} units...")
                self.executor.scroll(scroll_amt)
                time.sleep(3)
            return True
        else:
            print("\n  [Error] Could not confirm login. We might be stuck on a CAPTCHA or incorrect password.")
            self._see_and_log("final_verify_fail")
            return False

if __name__ == "__main__":
    import asyncio
    automator = TwitterAutomator()
    asyncio.run(automator.run("ever mlaudzi"))
