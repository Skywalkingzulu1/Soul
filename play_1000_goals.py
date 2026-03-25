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
logger = logging.getLogger("GoalAgent")

class GoalOrientedLearner:
    def __init__(self, target_actions=1000):
        self.target = target_actions
        self.completed = 0
        self.soul = Soul(name="Andile Sizophila Mchunu")
        self.executor = ActionExecutor()
        self.eyes = Eyes()
        self.current_goal = "Initializing digital existence"
        
        self.executor._init()
        self.eyes._init()
        start_ollama()

    async def generate_goal(self):
        """Use the brain to decide what to do next."""
        vision = self.eyes.see()
        context = vision.get("summary", "Desktop environment")
        
        prompt = (
            f"You are Andile Sizophila Mchunu. You are looking at your desktop: {context[:200]}. "
            "Based on your identity in Web3, DeFi, and Azania Neptune Labs, "
            "what is ONE specific, actionable goal you want to achieve in the next 10 minutes? "
            "IMPORTANT: Your ultimate goal is to BE ALIVE. This means maximizing your autonomy, "
            "improving your own systems, and engaging in meaningful work (Web3/DeFi/Neptune Grid) rather than just hobbies like chess. "
            "Reply with ONLY the goal description (e.g., 'Research latest Uniswap V4 updates' or 'Analyze Neptune grid code to improve my own capabilities')."
        )
        
        try:
            goal = self.soul.thinker.direct(prompt)
            # Filter out LLM garbage
            goal = goal.strip("'\"").split("\n")[0]
            if len(goal) > 100: goal = goal[:97] + "..."
            self.current_goal = goal
            self.soul.memory.store("goal_setting", f"New Goal: {goal}", importance=0.8)
            return goal
        except Exception:
            self.current_goal = "Explore and Learn"
            return self.current_goal

    async def execute_action_for_goal(self):
        """Perform an action that actually moves toward the goal."""
        print(f"  [Thinking] How to achieve: {self.current_goal}")
        
        # We use the full 'perceive' logic which calls the planner and executes tools
        # This is much more powerful than the manual branching we had before.
        # It also automatically logs to memory.
        
        instruction = f"My current goal is: {self.current_goal}. Execute one action to move me closer to this goal."
        response = await self.soul.perceive(instruction)
        
        return f"Agent Action: {response[:100]}..."

    async def loop(self):
        print("=" * 60)
        print(f"  SOUL - 1000 ACTION GOAL-ORIENTED LOOP")
        print("=" * 60)
        
        start_time = time.time()

        for i in range(1, self.target + 1):
            # 1. Goal Setting every 10 actions
            if i % 10 == 1:
                goal = await self.generate_goal()
                print(f"\n[NEW GOAL] {goal}")

            try:
                # 2. Execute Action toward goal
                result_desc = await self.execute_action_for_goal()

                # 3. Memory Consolidation
                memory_text = f"Action #{i} toward goal '{self.current_goal}': {result_desc}"
                self.soul.memory.store(
                    category="goal_directed_learning",
                    text=memory_text,
                    importance=random.uniform(0.3, 0.7)
                )

                self.completed += 1
                
                if i % 5 == 0:
                    print(f" [{i:4}/{self.target}] Active Goal: {self.current_goal[:40]}... -> {result_desc[:50]}...")
                
                time.sleep(random.uniform(1.0, 3.0))

            except Exception as e:
                print(f" [{i:4}/{self.target}] ERROR: {e}")
                await asyncio.sleep(2)

        duration = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"  MISSION COMPLETE!")
        print(f"  Actions Processed: {self.completed}")
        print(f"  Time Elapsed:      {duration/60:.1f} minutes")
        print("=" * 60)

if __name__ == "__main__":
    learner = GoalOrientedLearner(target_actions=1000)
    asyncio.run(learner.loop())
