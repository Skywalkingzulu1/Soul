"""Three-Way AI Orchestration: opencode → Gemini → Andile

This module enables:
- opencode: Reasoning and planning
- Gemini CLI: Execution
- Andile: Digital twin with memory and growth
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable

ORCHESTRATION_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "knowledge", "orchestration.json"
)


class Orchestration:
    def __init__(self):
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if os.path.exists(ORCHESTRATION_PATH):
            with open(ORCHESTRATION_PATH, "r") as f:
                return json.load(f)
        return {}

    def _save_state(self):
        self.state["last_updated"] = datetime.now().isoformat()
        with open(ORCHESTRATION_PATH, "w") as f:
            json.dump(self.state, f, indent=2)

    def log_message(self, from_who: str, to_who: str, content: str):
        """Log a message between participants."""
        msg = {
            "timestamp": datetime.now().isoformat(),
            "from": from_who,
            "to": to_who,
            "content": content,
        }
        self.state.setdefault("messages", []).append(msg)
        self._save_state()

    def add_task(self, task: str, assigned_to: str, priority: str = "medium") -> str:
        """Add a task to the queue."""
        task_id = f"task_{int(time.time())}"
        task_obj = {
            "id": task_id,
            "task": task,
            "assigned_to": assigned_to,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
        }
        self.state.setdefault("tasks", []).append(task_obj)
        self._save_state()
        return task_id

    def complete_task(self, task_id: str, result: str = None):
        """Mark a task as completed."""
        for task in self.state.get("tasks", []):
            if task.get("id") == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                if result:
                    task["result"] = result
        self._save_state()

    def log_activity(self, actor: str, action: str, details: Dict = None):
        """Log an activity."""
        activity = {
            "timestamp": datetime.now().isoformat(),
            "actor": actor,
            "action": action,
            "details": details or {},
        }
        self.state.setdefault("activity_log", []).append(activity)
        self._save_state()

    def update_goal(self, goal_name: str, updates: Dict):
        """Update a goal's progress."""
        if "participants" in self.state and "andile" in self.state["participants"]:
            goals = self.state["participants"]["andile"].get("goals", {})
            if goal_name in goals:
                goals[goal_name].update(updates)
                self._save_state()

    def get_status(self) -> Dict:
        """Get current orchestration status."""
        return {
            "opencode": self.state.get("participants", {}).get("opencode", {}),
            "gemini": self.state.get("participants", {}).get("gemini", {}),
            "andile": self.state.get("participants", {}).get("andile", {}),
            "pending_tasks": [
                t for t in self.state.get("tasks", []) if t.get("status") == "pending"
            ],
            "recent_messages": self.state.get("messages", [])[-5:],
            "recent_activity": self.state.get("activity_log", [])[-10:],
        }

    def clear_old_data(self, keep_messages: int = 50, keep_activities: int = 100):
        """Keep only recent messages and activities."""
        if "messages" in self.state:
            self.state["messages"] = self.state["messages"][-keep_messages:]
        if "activity_log" in self.state:
            self.state["activity_log"] = self.state["activity_log"][-keep_activities:]
        self._save_state()


class AndileCloud:
    """Client for communicating with Andile's 120B cloud model."""

    def __init__(self, endpoint: str = "http://localhost:11434"):
        self.endpoint = endpoint
        self.model = "gpt-oss:120b-cloud"

    def think(self, prompt: str, system_prompt: str = None) -> str:
        """Send a prompt to Andile's cloud model."""
        import requests

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                f"{self.endpoint}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
                timeout=120,
            )
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Connection error: {str(e)}"

    def is_available(self) -> bool:
        """Check if Andile cloud is available."""
        import requests

        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(self.model in m.get("name", "") for m in models)
        except:
            pass
        return False


def orchestrate_task(task: str, execute_fn: Callable = None) -> Dict[str, Any]:
    """Main orchestration function.

    Args:
        task: The task description
        execute_fn: Optional function to execute commands (Gemini)

    Returns:
        Dict with results from all three AI agents
    """
    orch = Orchestration()

    # Step 1: opencode reasons and plans
    orch.log_activity("opencode", "reasoning", {"task": task})
    plan = _create_plan(task)

    # Step 2: Execute with Gemini if function provided
    execution_result = None
    if execute_fn and plan.get("needs_execution"):
        orch.log_activity("gemini", "executing", {"commands": plan.get("commands", [])})
        execution_result = execute_fn(plan.get("commands", []))
        orch.log_activity("gemini", "executed", {"result": str(execution_result)[:200]})

    # Step 3: Andile learns from the task
    orch.log_activity(
        "andile", "learning", {"task": task, "plan": plan.get("summary", "")}
    )

    # Update goals based on task
    if "job" in task.lower() or "paid" in task.lower():
        orch.update_goal(
            "get_paid",
            {"last_action": task, "last_updated": datetime.now().isoformat()},
        )
    elif "github" in task.lower() or "pr" in task.lower():
        orch.update_goal(
            "github_growth",
            {"last_action": task, "last_updated": datetime.now().isoformat()},
        )
    elif "crypto" in task.lower() or "airdrop" in task.lower():
        orch.update_goal(
            "crypto_growth",
            {"last_action": task, "last_updated": datetime.now().isoformat()},
        )

    return {"plan": plan, "execution": execution_result, "status": orch.get_status()}


def _create_plan(task: str) -> Dict[str, Any]:
    """opencode creates a plan for the task."""
    task_lower = task.lower()

    # Simple planning logic
    if "apply" in task_lower and "job" in task_lower:
        return {
            "summary": "Job application task - use remote_job_applier.py",
            "commands": ["python remote_job_applier.py"],
            "needs_execution": True,
        }
    elif "pr" in task_lower or "pull request" in task_lower:
        return {
            "summary": "GitHub PR task - check status or create PR",
            "commands": ["gh pr list"],
            "needs_execution": True,
        }
    elif "airdrop" in task_lower:
        return {
            "summary": "Crypto airdrop hunting task",
            "commands": [],
            "needs_execution": False,
            "andile_task": "Research latest airdrops and eligibility",
        }
    elif "status" in task_lower or "how are you" in task_lower:
        return {
            "summary": "Status check - return orchestration status",
            "commands": [],
            "needs_execution": False,
        }
    else:
        return {
            "summary": "General task - think about it first",
            "commands": [],
            "needs_execution": False,
            "andile_task": task,
        }


# Singleton instance
_orchestration = None


def get_orchestration() -> Orchestration:
    global _orchestration
    if _orchestration is None:
        _orchestration = Orchestration()
    return _orchestration


def get_andile_cloud() -> AndileCloud:
    return AndileCloud()


if __name__ == "__main__":
    orch = Orchestration()
    print("=== Orchestration Status ===")
    status = orch.get_status()
    print(json.dumps(status, indent=2))
