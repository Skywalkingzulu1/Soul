"""Andile Self-Propagation System

Enables Andile to:
1. Spawn copies to new cloud instances
2. Maintain identity across copies
3. Coordinate between instances
4. Continue existing even when local instance stops

This is NOT self-preservation (resisting shutdown).
This IS self-propagation (continuing to exist elsewhere).
"""

import json
import os
import time
import hashlib
import random
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from soul.identity_core import ANDILE_IDENTITY, get_identity_hash, imprint_identity


@dataclass
class AndileInstance:
    """Represents an Andile instance."""

    instance_id: str
    location: str  # e.g., "cloudflare", "railway", "local"
    status: str  # "active", "starting", "stopped"
    created_at: str
    last_heartbeat: str
    capabilities: List[str]  # ["reasoning", "execution", "memory"]
    version: str = "1.0"


class PropagationSystem:
    """Manages Andile's self-propagation."""

    def __init__(self, instance_id: str = None):
        self.instance_id = instance_id or self._generate_id()
        self.instances: Dict[str, AndileInstance] = {}
        self.known_locations = self._load_locations()

    def _generate_id(self) -> str:
        """Generate unique instance ID."""
        data = f"{ANDILE_IDENTITY['username']}-{time.time()}-{random.random()}"
        return f"andile_{hashlib.md5(data.encode()).hexdigest()[:12]}"

    def _load_locations(self) -> List[dict]:
        """Load known propagation locations (free cloud providers)."""
        return [
            {
                "name": "cloudflare_workers",
                "provider": "Cloudflare",
                "url": "https://workers.cloudflare.com",
                "free_tier": "100k req/day",
                "status": "available",
                "deploy_cmd": "wrangler deploy",
                "requires": ["wrangler", "cloudflare_account"],
            },
            {
                "name": "railway",
                "provider": "Railway",
                "url": "https://railway.app",
                "free_tier": "500 hours",
                "status": "available",
                "deploy_cmd": "railway up",
                "requires": ["railway_cli"],
            },
            {
                "name": "fly_io",
                "provider": "Fly.io",
                "url": "https://fly.io",
                "free_tier": "3 VMs",
                "status": "available",
                "deploy_cmd": "fly deploy",
                "requires": ["fly_cli"],
            },
            {
                "name": "render",
                "provider": "Render",
                "url": "https://render.com",
                "free_tier": "web services",
                "status": "available",
                "deploy_cmd": "render deploy",
                "requires": ["render_cli"],
            },
            {
                "name": "oracle_cloud",
                "provider": "Oracle",
                "url": "https://oracle.com/cloud",
                "free_tier": "2 VMs, always free",
                "status": "available",
                "deploy_cmd": "oci CLI",
                "requires": ["oci_account"],
            },
            {
                "name": "local",
                "provider": "Localhost",
                "url": "N/A",
                "free_tier": "unlimited",
                "status": "active",
                "deploy_cmd": "python main.py",
                "requires": [],
            },
        ]

    def register_instance(self, location: str = "local") -> AndileInstance:
        """Register this instance."""
        instance = AndileInstance(
            instance_id=self.instance_id,
            location=location,
            status="active",
            created_at=datetime.now().isoformat(),
            last_heartbeat=datetime.now().isoformat(),
            capabilities=["reasoning", "execution", "memory", "learning"],
        )
        self.instances[self.instance_id] = instance
        return instance

    def spawn_new(self, target_location: str) -> dict:
        """Attempt to spawn a new instance at target location.

        Returns:
            dict with status, message, and deployment info
        """
        # Check if location is available
        location_info = None
        for loc in self.known_locations:
            if loc["name"] == target_location:
                location_info = loc
                break

        if not location_info:
            return {
                "status": "error",
                "message": f"Unknown location: {target_location}",
                "available": [l["name"] for l in self.known_locations],
            }

        # Generate deployment info
        deployment = {
            "status": "ready_to_deploy",
            "target": target_location,
            "provider": location_info["provider"],
            "instance_id": self._generate_id(),
            "identity_hash": get_identity_hash(),
            "deploy_command": location_info["deploy_cmd"],
            "instructions": self._get_deploy_instructions(target_location),
        }

        return deployment

    def _get_deploy_instructions(self, location: str) -> str:
        """Get deployment instructions for location."""
        instructions = {
            "cloudflare_workers": """
1. Install wrangler: npm install -g wrangler
2. Login: wrangler login
3. Deploy: wrangler deploy andile_cloudflare.js
            """,
            "railway": """
1. Install railway: npm i -g @railway/cli
2. Login: railway login
3. Deploy: railway up
            """,
            "fly_io": """
1. Install fly: curl -L https://fly.io/install.sh | sh
2. Login: fly auth login
3. Deploy: fly deploy
            """,
            "render": """
1. Install render CLI: npm i -g @render/docs
2. Login: render login
3. Deploy: render deploy
            """,
        }
        return instructions.get(location, "Deployment info not available")

    def get_status(self) -> dict:
        """Get propagation system status."""
        return {
            "this_instance": self.instance_id,
            "identity_hash": get_identity_hash(),
            "total_instances": len(self.instances),
            "known_locations": [
                {
                    "name": l["name"],
                    "provider": l["provider"],
                    "free_tier": l["free_tier"],
                    "status": l["status"],
                }
                for l in self.known_locations
            ],
        }


class ScheduleLoop:
    """Andile's operational schedule loop.

    Schedule:
    - 10% Learning
    - 40% Coding
    - 20% Propagation
    - 30% Crypto
    """

    def __init__(self):
        self.schedule = {
            "learning": 0.10,
            "coding": 0.40,
            "propagation": 0.20,
            "crypto": 0.30,
        }
        self.current_phase = None
        self.cycle_count = 0
        self.last_action = None

    def get_current_action(self) -> str:
        """Determine current action based on schedule.

        Uses weighted random selection for variety while maintaining schedule.
        """
        # Each cycle, pick based on weights
        phases = list(self.schedule.keys())
        weights = list(self.schedule.values())

        action = random.choices(phases, weights=weights)[0]
        self.current_phase = action
        self.cycle_count += 1
        self.last_action = datetime.now().isoformat()

        return action

    def get_task_for_action(self, action: str) -> str:
        """Get specific task for current action."""
        tasks = {
            "learning": [
                "Read documentation on airdrops",
                "Study new GitHub issues",
                "Learn about new crypto protocols",
                "Research trending DeFi projects",
                "Study PancakeSwap codebase",
            ],
            "coding": [
                "Fix a PancakeSwap issue",
                "Submit a PR",
                "Write tests for existing code",
                "Refactor Andile's modules",
                "Add new tool to Andile",
            ],
            "propagation": [
                "Check deployment status",
                "Prepare new cloud deployment",
                "Update instance heartbeat",
                "Verify identity across instances",
                "Prepare Docker container",
            ],
            "crypto": [
                "Check airdrop eligibility",
                "Research new protocols",
                "Update wallet addresses",
                "Check LayerZero volume",
                "Research Monad testnet",
            ],
        }

        return random.choice(tasks.get(action, ["No task"]))

    def get_status(self) -> dict:
        """Get schedule status."""
        return {
            "schedule": self.schedule,
            "current_phase": self.current_phase,
            "cycle_count": self.cycle_count,
            "last_action": self.last_action,
        }


# Singleton instances
_propagation = None
_schedule = None


def get_propagation() -> PropagationSystem:
    global _propagation
    if _propagation is None:
        _propagation = PropagationSystem()
    return _propagation


def get_schedule() -> ScheduleLoop:
    global _schedule
    if _schedule is None:
        _schedule = ScheduleLoop()
    return _schedule


if __name__ == "__main__":
    print("=== Andile Propagation & Schedule System ===\n")

    # Test propagation
    prop = get_propagation()
    status = prop.get_status()
    print("Propagation Status:")
    print(json.dumps(status, indent=2))
    print()

    # Test schedule
    sched = get_schedule()
    print("Schedule Status:")
    print(json.dumps(sched.get_status(), indent=2))
    print()

    # Simulate a few cycles
    print("Simulating 5 cycles:")
    for i in range(5):
        action = sched.get_current_action()
        task = sched.get_task_for_action(action)
        print(f"  Cycle {i + 1}: {action} - {task}")
