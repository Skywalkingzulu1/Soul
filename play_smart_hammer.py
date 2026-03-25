import time
import subprocess
import logging
import os
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartHammer")

class TwitterAutomator:
    def __init__(self):
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def _wait_and_verify(self, target_texts, timeout=15, description=""):
        """Wait for any of the target texts to appear and return coordinates."""
        if isinstance(target_texts, str):
            target_texts = [target_texts]
            
        print(f"  [Verify] Waiting for: {target_texts} ({description})...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            vision = self.eyes.see()
            all_text = vision.get("text", "").lower()
            
            # Check for targets
            for target in target_texts:
                matches = [box for box in vision.get("text_boxes", []) if target.lower() in box["text"].lower()]
                if matches:
                    box = matches[0]
                    center_x = box["x"] + box["w"] // 2
                    center_y = box["y"] + box["h"] // 2
                    print(f"  [Found] '{target}' at ({center_x}, {center_y})")
                    return center_x, center_y, target
            
            # Handle the Google Obstruction specifically
            if "sign in to x" in all_text or "google" in all_text:
                print("  [Obstruction] Google Login detected. Attempting to click outside or press ESC...")
                # Try ESC first
                self.executor.press("escape")
                # Also try clicking top left of the screen (usually safe) to focus away
                self.executor.click(100, 100)
                time.sleep(2)
                
            time.sleep(2)
        return None

    async def run(self, username):
        print("=" * 60)
        print("  SOUL - SMART HAMMER TWITTER AUTOMATION")
        print("=" * 60)

        # Try opening in Private/Incognito mode to avoid Google popups
        print("\n[Step 1] Opening Twitter in Private Mode...")
        # Try MS Edge Private first (since it's common on Windows), then Chrome Incognito
        try:
            subprocess.Popen(['msedge', '--inprivate', 'https://twitter.com/login'])
        except Exception:
            subprocess.Popen(['chrome', '--incognito', 'https://twitter.com/login'])
        
        # 2. Wait for Login Page
        login_pos = self._wait_and_verify(["Phone, email", "username"], timeout=30, description="Username field")
        if not login_pos:
            print("  [Error] Could not find login field. Trying one last 'Blind Click' strategy...")
            # On 1920x1080, the username field is often around center
            self.executor.click(960, 450) 
            time.sleep(1)
        else:
            self.executor.click(login_pos[0], login_pos[1])

        # 3. Enter Username
        print(f"\n[Step 2] Entering Username: {username}...")
        self.executor.type_text(username, base_interval=0.1)
        self.executor.press('enter')
        
        # 4. Wait for Password
        pass_pos = self._wait_and_verify(["Password"], timeout=15, description="Password field")
        if not pass_pos:
            print("  [Error] Failed to reach password screen.")
            self.eyes.save_screenshot(os.path.join(self.screenshot_dir, "hammer_fail.png"))
            return False
        
        print("\n[Step 3] Password Screen reached. HUMAN INTERVENTION START.")
        print("  PLEASE ENTER PASSWORD AND LOG IN NOW.")
        # Wait longer for manual entry
        for i in range(20):
            print(f"  Waiting... {20-i}s", end="\r")
            time.sleep(1)

        # 5. Final Feed Check
        print("\n\n[Step 4] Verifying Home Feed...")
        home_pos = self._wait_and_verify(["Home", "Explore", "Notifications"], timeout=20, description="Twitter Feed")
        if home_pos:
            print("\n  [SUCCESS] Digital Twin has verified the login state.")
            print("  Starting human-like interaction...")
            for _ in range(5):
                self.executor.scroll(-1000)
                time.sleep(random.uniform(2, 5))
            return True
        else:
            print("\n  [Final Check] Could not confirm feed. Manual check recommended.")
            return False

if __name__ == "__main__":
    import asyncio
    import random
    automator = TwitterAutomator()
    asyncio.run(automator.run("ever mlaudzi"))
