"""Agentic loop — Perceive → Understand → Plan → Act → Reflect.

The core autonomous behavior loop that makes the soul "agentic":
it sees the screen, understands what's happening, decides what to do,
does it, and learns from the result.
"""

import asyncio
import logging
import time

logger = logging.getLogger(__name__)


class AgenticLoop:
    """Autonomous perceive-plan-act loop."""

    def __init__(self, soul):
        self.soul = soul
        self.running = False
        self.goal = ""
        self.cycle_count = 0
        self.max_cycles = 10  # Safety limit

    async def run(self, goal, max_cycles=10):
        """Run the agentic loop for a specific goal.

        Args:
            goal: What to accomplish
            max_cycles: Maximum perception-action cycles

        Returns:
            dict with final state and results
        """
        self.goal = goal
        self.max_cycles = max_cycles
        self.cycle_count = 0
        self.running = True

        results = []

        logger.info(f"Starting agentic loop: {goal}")

        while self.running and self.cycle_count < self.max_cycles:
            self.cycle_count += 1
            logger.info(f"Cycle {self.cycle_count}/{self.max_cycles}")

            try:
                result = await self._cycle()
                results.append(result)

                if result.get("done"):
                    logger.info(f"Goal achieved: {goal}")
                    break

            except Exception as e:
                logger.error(f"Cycle {self.cycle_count} error: {e}")
                results.append({"cycle": self.cycle_count, "error": str(e)})

            await asyncio.sleep(1)

        self.running = False

        return {
            "goal": self.goal,
            "cycles": self.cycle_count,
            "results": results,
            "completed": any(r.get("done") for r in results),
        }

    async def _cycle(self):
        """Single perceive-plan-act cycle."""
        from soul.vision.eyes import Eyes
        from soul.agentic.perceive import analyze_screen, decide_action
        from soul.agentic.act import ActionExecutor

        eyes = Eyes()
        executor = ActionExecutor()

        # 1. PERCEIVE
        logger.info(f"  [1] Perceiving screen...")
        vision = eyes.see()
        screen_text = vision.get("text", "")

        # 2. UNDERSTAND
        logger.info(f"  [2] Analyzing...")
        analysis = analyze_screen(screen_text, context=f"Goal: {self.goal}")
        logger.info(f"  Analysis: {analysis[:100]}...")

        # 3. PLAN
        logger.info(f"  [3] Deciding action...")
        action = decide_action(screen_text, analysis, goal=self.goal)
        logger.info(f"  Action: {action['action']} - {action['reason'][:50]}")

        # 4. ACT
        logger.info(f"  [4] Executing: {action['action']}...")
        executed = False
        if action["action"] == "click" and action.get("target"):
            executed = executor.click()
        elif action["action"] == "type" and action.get("target"):
            executed = executor.type_text(action["target"])
        elif action["action"] == "scroll":
            executed = executor.scroll(-3)
        elif action["action"] == "done":
            return {"cycle": self.cycle_count, "action": "done", "done": True}
        else:
            logger.info(f"  No action taken (action={action['action']})")

        # 5. REFLECT
        self.soul.memory.store(
            "agentic_cycle",
            f"Cycle {self.cycle_count}: {action['action']} | Analysis: {analysis[:100]}",
            importance=0.6,
        )

        return {
            "cycle": self.cycle_count,
            "action": action["action"],
            "analysis": analysis[:200],
            "executed": executed,
            "done": action["action"] == "done",
        }

    def stop(self):
        self.running = False

    def get_state(self):
        return {
            "running": self.running,
            "goal": self.goal,
            "cycle": self.cycle_count,
            "max_cycles": self.max_cycles,
        }
