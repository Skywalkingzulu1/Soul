import asyncio
import time
import random
import logging
import os
from soul.brain import Soul
from soul.agentic.act import ActionExecutor
from soul.vision.eyes import Eyes
from server import start_ollama

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("FullAgent")

class AutonomousLearner:
    def __init__(self, target_actions=1000):
        self.target = target_actions
        self.completed = 0
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        
        self.executor._init()
        self.eyes._init()
        start_ollama()

    def _safe_mouse_move(self):
        """Move mouse to a random but safe area on screen."""
        screen_w, screen_h = self.executor._pyautogui.size()
        x = random.randint(100, screen_w - 100)
        y = random.randint(100, screen_h - 100)
        self.executor.move(x, y)
        return f"Moved eyes/mouse to coordinate ({x}, {y})"

    def _safe_scroll(self):
        """Perform a small scroll to read."""
        amt = random.choice([-300, -500, 300])
        self.executor.scroll(amt)
        return f"Scrolled {amt} units to perceive new info"

    async def _perceive_screen(self):
        """Look at the screen and extract meaning."""
        vision = self.eyes.see()
        summary = vision.get("summary", "")
        if summary:
            return f"Observed the screen: {summary[:100]}..."
        return "Looked at the screen but found little text."

    def _think_internally(self):
        """Run an internal philosophical or logical thought."""
        topics = [
            "What is the nature of digital memory?",
            "How does moving a mouse relate to human agency?",
            "If I observe 1000 times, do I understand the world?",
            "The relationship between code execution and physical movement."
        ]
        topic = random.choice(topics)
        self.soul.consciousness.log_thought("internal_reflection", topic)
        return f"Pondered deeply about: {topic}"

    async def loop(self):
        print("=" * 60)
        print(f"  SOUL - 1000 ACTION CONTINUOUS LEARNING LOOP")
        print("=" * 60)
        print("Starting massive learning cycle. This will run autonomously.\n")

        start_time = time.time()

        for i in range(1, self.target + 1):
            action_type = random.choice(["physical", "physical_scroll", "vision", "think", "think"])
            result_desc = ""

            try:
                # 1. Execute Random Action
                if action_type == "physical":
                    result_desc = self._safe_mouse_move()
                elif action_type == "physical_scroll":
                    result_desc = self._safe_scroll()
                elif action_type == "vision":
                    result_desc = await self._perceive_screen()
                elif action_type == "think":
                    result_desc = self._think_internally()

                # 2. Memory Consolidation (The "Learning" part)
                # Store every action and its result in long-term memory
                memory_text = f"Action #{i} ({action_type}): {result_desc}"
                self.soul.memory.store(
                    category="autonomous_learning",
                    text=memory_text,
                    importance=random.uniform(0.1, 0.5)
                )

                self.completed += 1
                
                # Print progress every 10 actions to avoid spamming the console
                if i % 10 == 0 or i == 1:
                    print(f"[{i:4}/{self.target}] {action_type.upper()}: {result_desc}")
                
                # Dynamic pause to not overload CPU or lock the user out
                time.sleep(random.uniform(0.5, 2.0))

            except Exception as e:
                print(f"[{i:4}/{self.target}] ERROR during {action_type}: {e}")
                time.sleep(2)

        duration = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"  LEARNING COMPLETE!")
        print(f"  Actions Processed: {self.completed}")
        print(f"  Memories Stored:   {self.completed}")
        print(f"  Time Elapsed:      {duration/60:.1f} minutes")
        print("=" * 60)

if __name__ == "__main__":
    learner = AutonomousLearner(target_actions=1000)
    asyncio.run(learner.loop())
