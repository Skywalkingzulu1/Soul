import asyncio
import time
import logging
import os
from soul.brain import Soul
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemExplorer")

class SystemExplorer:
    def __init__(self):
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()

    async def learn_route(self, route_name, description, action_coro):
        print(f"\n[Route] Exploring: {route_name}")
        print(f"        Action: {description}")
        
        try:
            # 1. Navigate to the route
            if asyncio.iscoroutine(action_coro):
                await action_coro
            else:
                action_coro()
            
            # 2. Let the UI settle and "See"
            time.sleep(2.5)
            vision = self.eyes.see()
            summary = vision.get("summary", "Visual data captured.")
            full_text = vision.get("text", "")
            
            # 3. Consolidate into Memory (Learning)
            memory_content = f"Route Mapping [{route_name}]: {summary}\nKey Details: {full_text[:300]}"
            self.soul.memory.store(
                memory_type="system_map",
                content=memory_content,
                importance=0.7
            )
            
            print(f"        Status: Route mapped and stored in memory.")
            return True
        except Exception as e:
            print(f"        Status: Failed to map route: {e}")
            return False

    async def main(self):
        print("=" * 60)
        print("  SOUL - SYSTEM EXPLORATION & ROUTE LEARNING")
        print("  Mode: READ-ONLY / OBSERVATIONAL")
        print("=" * 60)

        # Route 1: Taskbar Scan
        screen_w, screen_h = self.executor._pyautogui.size()
        await self.learn_route("Taskbar", "Hovering over system taskbar", 
            asyncio.to_thread(self.executor.move, screen_w // 2, screen_h - 20))

        # Route 2: Start Menu Pinned Apps
        await self.learn_route("Start Menu", "Opening Start Menu to scan pinned apps", 
            asyncio.to_thread(self.executor.press, "win"))
        self.executor.press("win") # Close it after scanning

        # Route 3: File System (User Folder)
        await self.learn_route("File System", "Opening User folder via shortcut", 
            asyncio.to_thread(self.executor.hotkey, "win", "e"))
        time.sleep(1)
        self.executor.hotkey("alt", "f4") # Close Explorer

        # Route 4: Display Settings
        await self.learn_route("Display Settings", "Navigating to Display via Settings", 
            asyncio.to_thread(self.executor.hotkey, "win", "i"))
        self.executor.type_text("display", 0.1)
        self.executor.press("enter")
        time.sleep(2)
        self.executor.hotkey("alt", "f4") # Close Settings

        # Route 5: System Tray (Clock/Calendar)
        await self.learn_route("Clock/Calendar", "Opening system calendar for context", 
            asyncio.to_thread(self.executor.hotkey, "win", "alt", "d"))
        self.executor.hotkey("win", "alt", "d") # Close it

        # Route 6: Network Status
        await self.learn_route("Network Status", "Checking network flyout", 
            asyncio.to_thread(self.executor.hotkey, "win", "a"))
        self.executor.hotkey("win", "a") # Close it

        # Route 7: Desktop Icons
        await self.learn_route("Desktop Icons", "Moving to top-left to scan desktop icons", 
            asyncio.to_thread(self.executor.move, 100, 100))

        # Route 8: Power & Sleep
        await self.learn_route("Power Settings", "Observing power state via Start search", 
            asyncio.to_thread(self.executor.press, "win"))
        self.executor.type_text("power sleep", 0.1)
        time.sleep(1)
        self.executor.press("esc")

        # Route 9: System Information
        await self.learn_route("System Info", "Reading hardware summary", 
            asyncio.to_thread(subprocess.Popen, ["msinfo32"]))
        time.sleep(2)
        self.executor.hotkey("alt", "f4") # Close msinfo32

        # Route 10: Final Consolidation
        print("\n[Finalizing Map] Summarizing all learned routes...")
        status = self.soul.status()
        self.soul.memory.store("system_map", f"Full system exploration complete. Status: {status}", importance=0.9)
        
        print("\n" + "=" * 60)
        print("  EXPLORATION COMPLETE: 10 ROUTES LEARNED")
        print("=" * 60)

import subprocess
if __name__ == "__main__":
    explorer = SystemExplorer()
    asyncio.run(explorer.main())
