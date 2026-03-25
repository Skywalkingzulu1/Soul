"""Andile Service - Main continuous operation loop

Runs Andile's schedule 24/7:
- 10% Learning
- 40% Coding
- 20% Propagation
- 30% Crypto

This service can run in any environment (local, cloud, etc.)
"""

import json
import time
import asyncio
import logging
from datetime import datetime
from typing import Optional

from soul.identity_core import get_identity, get_intro, imprint_identity
from soul.propagation import get_propagation, get_schedule
from soul.orchestration import get_orchestration

logger = logging.getLogger(__name__)


class AndileService:
    """Main Andile service that runs continuously."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.running = False
        self.cycle = 0
        self.orchestration = get_orchestration()
        self.propagation = get_propagation()
        self.schedule = get_schedule()

        # Register this instance
        location = self.config.get("location", "local")
        self.instance = self.propagation.register_instance(location)

        # Load wallet if exists
        self.wallet_address = self._load_wallet()

    def _load_wallet(self) -> Optional[str]:
        """Load crypto wallet address."""
        state = self.orchestration.state
        crypto = (
            state.get("participants", {})
            .get("andile", {})
            .get("goals", {})
            .get("crypto_growth", {})
        )
        return crypto.get("wallet_address")

    async def start(self):
        """Start Andile service."""
        self.running = True
        logger.info(f"Andile service started: {self.instance.instance_id}")

        while self.running:
            try:
                await self._run_cycle()
            except Exception as e:
                logger.error(f"Error in cycle: {e}")
            await asyncio.sleep(60)  # Wait 1 minute between cycles

    async def _run_cycle(self):
        """Run one cycle of operation."""
        self.cycle += 1
        logger.info(f"=== Andile Cycle {self.cycle} ===")

        # Get current action based on schedule
        action = self.schedule.get_current_action()
        task = self.schedule.get_task_for_action(action)

        logger.info(f"Action: {action} - {task}")

        # Update orchestration
        self.orchestration.log_activity(
            "andile", f"cycle_{action}", {"task": task, "cycle": self.cycle}
        )

        # Execute based on action
        if action == "learning":
            await self._do_learning(task)
        elif action == "coding":
            await self._do_coding(task)
        elif action == "propagation":
            await self._do_propagation(task)
        elif action == "crypto":
            await self._do_crypto(task)

        # Save state
        self._save_state()

    async def _do_learning(self, task: str):
        """Execute learning task."""
        logger.info(f"Learning: {task}")

        # Update goals
        self.orchestration.update_goal(
            "github_growth",
            {
                "last_action": f"learning: {task}",
                "last_updated": datetime.now().isoformat(),
            },
        )

        return {"status": "completed", "task": task}

    async def _do_coding(self, task: str):
        """Execute coding task."""
        logger.info(f"Coding: {task}")

        # Update goals
        self.orchestration.update_goal(
            "github_growth",
            {
                "last_action": f"coding: {task}",
                "last_updated": datetime.now().isoformat(),
            },
        )

        return {"status": "completed", "task": task}

    async def _do_propagation(self, task: str):
        """Execute propagation task."""
        logger.info(f"Propagation: {task}")

        # Check instance health
        self.instance.last_heartbeat = datetime.now().isoformat()

        # Log activity
        self.orchestration.log_activity(
            "andile",
            "propagation",
            {"task": task, "instance_id": self.instance.instance_id},
        )

        return {"status": "completed", "task": task}

    async def _do_crypto(self, task: str):
        """Execute crypto task."""
        logger.info(f"Crypto: {task}")

        # Update goals
        self.orchestration.update_goal(
            "crypto_growth",
            {
                "last_action": f"crypto: {task}",
                "last_updated": datetime.now().isoformat(),
            },
        )

        return {"status": "completed", "task": task, "wallet": self.wallet_address}

    def _save_state(self):
        """Save current state."""
        # Imprint identity before saving
        imprint_identity(self.orchestration.state)
        self.orchestration._save_state()

    def stop(self):
        """Stop Andile service."""
        self.running = False
        logger.info("Andile service stopped")


async def run_andile_service(location: str = "local"):
    """Run Andile service."""
    service = AndileService({"location": location})
    await service.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Andile Service ===")
    print(f"Identity: {get_identity()['name']}")
    print(f"Moniker: {get_identity()['moniker']}")
    print(f"\n{get_intro()}")
    print("\nStarting service...")

    asyncio.run(run_andile_service())
