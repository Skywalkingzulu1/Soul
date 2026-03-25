import time
import logging
import os
import random
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HumanDesktopDemo")

class HumanAutomator:
    def __init__(self):
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def _human_pause(self, min_s=1.0, max_s=2.5):
        """Simulate a human thinking or waiting for a UI response."""
        time.sleep(random.uniform(min_s, max_s))

    async def run(self):
        print("=" * 60)
        print("  SOUL - HUMAN DESKTOP INTERACTION DEMO")
        print("=" * 60)

        # 1. Initial Scan
        print("\n[Phase 1] Scanning environment...")
        vision = self.eyes.see()
        print(f"  [Vision] Desktop analyzed. Summary: {vision.get('summary', 'General desktop UI')[:100]}...")

        # 2. Open Notepad via Start Menu
        print("\n[Phase 2] Opening Notepad (Start Menu Navigation)...")
        self.executor.press("win")
        self._human_pause(0.8, 1.2)
        self.executor.type_text("notepad", base_interval=0.08)
        self._human_pause(0.5, 1.0)
        self.executor.press("enter")
        
        print("  Waiting for Notepad to initialize...")
        self._human_pause(2.0, 3.0)

        # 3. Creative Typing
        print("\n[Phase 3] Generating and typing content...")
        message = (
            "Hello, this is Andile's digital twin.\n\n"
            "I am currently exploring the desktop environment using human-like mouse "
            "and keyboard dynamics. I can see what is happening, I can plan my "
            "movements, and I can reflect on my actions.\n\n"
            "Status: Operating with world-class precision.\n"
            "Time: " + time.strftime("%H:%M:%S")
        )
        self.executor.type_text(message, base_interval=0.04)
        self._human_pause(1.5, 2.5)

        # 4. Window Management (Moving Notepad)
        print("\n[Phase 4] Moving the window (Human-like drag simulation)...")
        # Click the title bar area (approximate based on standard Notepad position)
        self.executor.move(400, 150) # Move to title bar
        self._human_pause(0.3, 0.6)
        # Dragging isn't a single primitive in our Executor, so we'll simulate it with mouseDown/move/mouseUp
        import pyautogui # Using internal ref for complex drag
        pyautogui.mouseDown(button='left')
        self.executor.move(800, 300, duration=1.2) # Smooth drag
        pyautogui.mouseUp(button='left')
        self._human_pause(1.0, 2.0)

        # 5. Exploring other UI elements
        print("\n[Phase 5] Exploring system tray / clock...")
        # Move mouse to the clock area (usually bottom right)
        screen_w, screen_h = self.executor._pyautogui.size()
        self.executor.move(screen_w - 50, screen_h - 20)
        self._human_pause(1.5, 2.5) # "Reading" the time

        # 6. Minimizing Window
        print("\n[Phase 6] Minimizing application...")
        # Standard Windows hotkey for minimizing current window
        self.executor.hotkey("win", "down")
        self._human_pause(0.5, 1.0)
        self.executor.hotkey("win", "down") # Press twice to minimize
        
        print("\n" + "=" * 60)
        print("  DEMO COMPLETE: PERFORMED 6 HUMAN-LEVEL TASKS")
        print("=" * 60)

if __name__ == "__main__":
    import asyncio
    automator = HumanAutomator()
    asyncio.run(automator.run())
