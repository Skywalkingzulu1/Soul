import asyncio
import time
import logging
import os
import random
from soul.brain import Soul
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BrowserExplorer")

class BrowserExplorer:
    def __init__(self):
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    async def learn_browser_route(self, route_name, description, target_keywords=None):
        print(f"\n[Browser Route] Exploring: {route_name}")
        print(f"                Action: {description}")
        
        try:
            # 1. Capture current view
            vision = self.eyes.see()
            text_boxes = vision.get("text_boxes", [])
            screen_text = vision.get("text", "").lower()
            
            # 2. Identify coordinates if keywords provided
            found_pos = None
            if target_keywords:
                for keyword in target_keywords:
                    matches = [box for box in text_boxes if keyword.lower() in box["text"].lower()]
                    if matches:
                        box = matches[0]
                        found_pos = (box["x"] + box["w"] // 2, box["y"] + box["h"] // 2)
                        print(f"                Found '{keyword}' at {found_pos}")
                        # Hover to "acknowledge" the route without clicking
                        self.executor.move(found_pos[0], found_pos[1], duration=0.8)
                        break
            
            # 3. Consolidate into Memory
            summary = vision.get("summary", "Browser UI captured.")
            memory_content = f"Browser Route [{route_name}]: {description}\nDetected Text: {screen_text[:200]}"
            if found_pos:
                memory_content += f"\nCoordinates: {found_pos}"
                
            self.soul.memory.store(
                memory_type="browser_map",
                content=memory_content,
                importance=0.6
            )
            
            print(f"                Status: Route '{route_name}' mapped.")
            time.sleep(1.5)
            return True
        except Exception as e:
            print(f"                Status: Failed to map browser route: {e}")
            return False

    async def main(self):
        print("=" * 60)
        print("  SOUL - BROWSER INTERFACE EXPLORATION")
        print("  Mode: OBSERVATIONAL / NON-DESTRUCTIVE")
        print("=" * 60)

        # Step 0: Initial Focus - Look for Chrome/Browser
        print("\n[Phase 0] Identifying browser window...")
        vision = self.eyes.see()
        if "chrome" in vision.get("text", "").lower() or "google" in vision.get("text", "").lower() or "tab" in vision.get("text", "").lower():
            print("  [Found] Browser window detected on screen.")
        else:
            print("  [Note] Browser not immediately obvious, scanning for general UI elements.")

        # Route 1: Address Bar / URL
        await self.learn_browser_route("Address Bar", "Locating the URL input field", ["https", "http", "search", ".com", ".org"])

        # Route 2: Navigation Buttons
        await self.learn_browser_route("Navigation Controls", "Locating Back, Forward, and Refresh area", ["reload", "refresh", "back", "forward"])

        # Route 3: Tab Strip
        await self.learn_browser_route("Tab Strip", "Scanning top area for open tabs", ["tab", "new tab", "x"])

        # Route 4: Utility Toolbar
        await self.learn_browser_route("Utility Area", "Locating Extensions and Menu", ["extensions", "menu", "profile", "settings"])

        # Route 5: Active Content Perception
        print("\n[Phase 5] Perceiving active page content...")
        # Move to center of screen to "read" the content
        screen_w, screen_h = self.executor._pyautogui.size()
        self.executor.move(screen_w // 2, screen_h // 2)
        time.sleep(1)
        vision = self.eyes.see()
        page_text = vision.get("text", "")
        
        self.soul.memory.store(
            memory_type="browser_context",
            content=f"Current Active Page Content Summary: {page_text[:500]}",
            importance=0.8
        )
        print("  Status: Page context learned and stored.")

        print("\n" + "=" * 60)
        print("  BROWSER EXPLORATION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    explorer = BrowserExplorer()
    asyncio.run(explorer.main())
