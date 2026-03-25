import asyncio
import time
import logging
import random
import pygetwindow as gw
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes
from soul.brain import Soul

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IterativeAgent")

class IterativeOrchestrator:
    def __init__(self):
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.executor._init()
        self.eyes._init()
        self.mission_log = []

    async def secure_focus(self):
        wins = [w for k in ["Chrome", "Google Chrome"] for w in gw.getWindowsWithTitle(k)]
        if wins:
            win = wins[0]
            if win.isMinimized: win.restore()
            win.activate()
            time.sleep(1.5)
            return True
        return False

    async def perceive_state(self):
        """Deep visual scan to understand current context."""
        vision = self.eyes.see()
        text = vision.get("text", "").lower()
        boxes = vision.get("text_boxes", [])
        return {"text": text, "boxes": boxes, "summary": vision.get("summary", "")}

    async def attempt_step(self, step_name, strategies, verify_keywords):
        """Try multiple strategies to achieve a sub-goal."""
        print(f"\n[Goal] {step_name}")
        
        for strategy_idx, strategy_func in enumerate(strategies):
            print(f"       -> Strategy {strategy_idx + 1}: {strategy_func.__name__}")
            
            # Execute Strategy
            await strategy_func()
            time.sleep(4) # Wait for UI response
            
            # VERIFY STATE
            state = await self.perceive_state()
            if any(k.lower() in state["text"] for k in verify_keywords):
                print(f"       -> [SUCCESS] State change verified by keywords.")
                self.mission_log.append(f"{step_name}: Success via {strategy_func.__name__}")
                return True
            
            # TROUBLESHOOT
            print(f"       -> [STUCK] Strategy failed. Diagnosing...")
            if "accept" in state["text"] or "agree" in state["text"]:
                print("          [Issue] Popup detected. Dismissing and retrying current strategy...")
                self.executor.click(960, 800) # Simple center-bottom click for popups
                time.sleep(2)
                # Retry same strategy once after fix
                await strategy_func()
                time.sleep(4)
                state = await self.perceive_state()
                if any(k.lower() in state["text"] for k in verify_keywords):
                    return True

        print(f"       -> [ABORT] All strategies for '{step_name}' failed. Shutting down mission to avoid zombie behavior.")
        self.mission_log.append(f"{step_name}: Critical Failure")
        return False

    async def run_iterative_mission(self):
        print("=" * 60)
        print("  SOUL - ITERATIVE PROBLEM-SOLVING MISSION")
        print("=" * 60)

        if not await self.secure_focus(): return

        # STEP 1: NAVIGATE
        async def strat_nav_direct():
            self.executor.hotkey("ctrl", "l")
            self.executor.type_text("https://www.gmx.com/registration/", base_interval=0.05)
            self.executor.press("enter")

        if not await self.attempt_step("Navigate to Form", [strat_nav_direct], ["First name", "Gender", "Birthday"]):
            return

        # STEP 2: INTERACT (First Name)
        async def strat_click_ocr():
            state = await self.perceive_state()
            for box in state["boxes"]:
                if "first name" in box["text"].lower():
                    self.executor.click(box["x"] + box["w"]//2, box["y"] + box["h"]//2)
                    self.executor.type_text("Andile", base_interval=0.06)
                    return
        
        async def strat_tab_navigation():
            self.executor.press("tab") # Try blind tabbing if OCR fails
            self.executor.type_text("Andile", base_interval=0.06)

        if not await self.attempt_step("Fill First Name", [strat_click_ocr, strat_tab_navigation], ["Andile"]):
            # If we get stuck here, it shuts down.
            print("\n[Final Report] Mission Aborted gracefully. Summary recorded in memory.")
            self.soul.memory.store("mission_failure", f"Iterative mission stopped at Identity stage. Log: {self.mission_log}", importance=0.5)
            return

        print("\n" + "=" * 60)
        print("  MISSION COMPLETE - ITERATIVE SUCCESS")
        print("=" * 60)

if __name__ == "__main__":
    agent = IterativeOrchestrator()
    asyncio.run(agent.run_iterative_mission())
