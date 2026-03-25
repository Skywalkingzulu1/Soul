import time
import subprocess
import logging
import os
import random
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartHammerV2")

class TwitterAutomator:
    def __init__(self):
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def _wait_and_verify(self, target_texts, timeout=15, description=""):
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
            
            # Dismiss popups
            if "google" in all_text or "sign in to x" in all_text:
                print("  [Obstruction] Dismissing Google popup...")
                self.executor.press("escape")
                time.sleep(1)
                
            time.sleep(2)
        return None

    async def run(self, username):
        print("=" * 60)
        print("  SOUL - SMART HAMMER TWITTER AUTOMATION (V2)")
        print("=" * 60)

        # Launch using 'start' which is more resilient on Windows
        print("\n[Step 1] Opening Twitter Login...")
        subprocess.Popen(['cmd', '/c', 'start', 'msedge', '--inprivate', 'https://twitter.com/login'])
        
        # 2. Wait for Login Page
        login_pos = self._wait_and_verify(["Phone, email", "username"], timeout=30, description="Username field")
        if not login_pos:
            print("  [Error] Could not find field. Trying to force click...")
            self.executor.click(960, 480) # Common vertical position
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
            self.eyes.save_screenshot(os.path.join(self.screenshot_dir, "hammer_fail_v2.png"))
            return False
        
        print("\n[Step 3] Password Screen reached. HUMAN INTERVENTION START.")
        print("  PLEASE ENTER PASSWORD AND LOG IN NOW.")
        for i in range(20):
            print(f"  Waiting... {20-i}s", end="\r")
            time.sleep(1)

        # 5. Final Feed Check
        print("\n\n[Step 4] Verifying Home Feed...")
        home_pos = self._wait_and_verify(["Home", "Explore", "Notifications"], timeout=25, description="Twitter Feed")
        if home_pos:
            print("\n  [SUCCESS] Digital Twin verified login.")
            for _ in range(5):
                self.executor.scroll(-1000)
                time.sleep(random.uniform(2, 5))
            return True
        else:
            print("\n  [Final Check] Could not confirm feed.")
            return False

if __name__ == "__main__":
    import asyncio
    automator = TwitterAutomator()
    asyncio.run(automator.run("ever mlaudzi"))
