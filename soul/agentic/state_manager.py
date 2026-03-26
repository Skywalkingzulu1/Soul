"""The Sentinel State Manager - Tracking the 24-Hour Cycle.

Ensures every repo is hit once every 24 hours and tracks 
hourly contribution progress across reloads.
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self, path="C:/Users/molel/Soul/soul_state.json"):
        self.path = Path(path)
        self.state = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "status": "Idle",
            "current_mission": "Waiting for Pulse",
            "last_run": None,
            "repo_queue": [],
            "completed_today": [],
            "hourly_contributions": 0,
            "outreach_sent": [],
            "activity_log": [],
            "tasks": [],
            "stats": {
                "jobs_applied": 0,
                "emails_sent": 0,
                "responses": 0,
                "income": 0,
                "prs_made": 0,
                "prs_merged": 0,
                "bounties_claimed": 0
            }
        }

    def save(self):
        self.state["last_run"] = datetime.now().isoformat()
        with open(self.path, "w") as f:
            json.dump(self.state, f, indent=4)

    def update_status(self, status, mission=None):
        """Update live status and log activity."""
        self.state["status"] = status
        if mission:
            self.state["current_mission"] = mission
        
        # Log to activity feed
        log_entry = {
            "actor": "andile",
            "action": f"{status}: {mission}" if mission else status,
            "timestamp": datetime.now().isoformat()
        }
        self.state.setdefault("activity_log", []).append(log_entry)
        # Keep last 50 logs
        self.state["activity_log"] = self.state["activity_log"][-50:]
        self.save()

    def add_task(self, task_name, type="repo", priority=3):
        """Add a task to the visible dashboard queue."""
        task = {
            "task": task_name,
            "type": type,
            "priority": priority,
            "status": "pending"
        }
        self.state.setdefault("tasks", []).append(task)
        self.save()

    def increment_stat(self, stat_name, amount=1):
        """Update numerical stats (e.g., prs_made, emails_sent)."""
        if "stats" not in self.state:
            self.state["stats"] = {}
        self.state["stats"][stat_name] = self.state["stats"].get(stat_name, 0) + amount
        self.save()

    def get_next_repos(self, count=3):
        """Get the next 3 repos for this hour's pulse."""
        if not self.state.get("repo_queue"):
            return []

        batch = self.state["repo_queue"][:count]
        self.state["repo_queue"] = self.state["repo_queue"][count:]
        self.state.setdefault("completed_today", []).extend(batch)
        return batch

    def refill_queue(self, all_repo_names):
        """Reset the queue with all repos, excluding already finished ones."""
        completed = self.state.get("completed_today", [])
        self.state["repo_queue"] = [r for r in all_repo_names if r not in completed]
        if not self.state["repo_queue"]: # Full reset
            self.state["repo_queue"] = all_repo_names
            self.state["completed_today"] = []
        self.save()
