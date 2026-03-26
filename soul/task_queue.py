"""Task Queue System - Manages Andile's execution queue

Priority Order:
1. GITHUB (high) - Quality PRs, bug fixes, bounties
2. CRYPTO (medium-high) - Airdrops, DeFi, wallet management
3. JOBS (medium) - Applications (hourly only)
4. RESEARCH (low) - 5% of time for learning/testing
5. SYSTEM (lowest) - Maintenance, heartbeats

Task Types:
- github_issue: Find and fix issues in target repos
- github_pr: Submit PR with quality code
- bounty_claim: Claim GitHub/open-source bounties
- airdrop_check: Check airdrop eligibility
- airdrop_claim: Execute airdrop claims
- job_apply: Send job application email
- job_followup: Send follow-up email
- research: Lab testing and learning
- system: Health checks, maintenance
"""

import json
import os
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum
from threading import Lock
from dataclasses import dataclass, asdict

from soul.core.logger import setup_logger

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
QUEUE_FILE = BASE_DIR / "knowledge" / "task_queue.json"


class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    IDLE = 5


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"  # Waiting for rate limit


class TaskType(Enum):
    # GitHub tasks (highest priority)
    GITHUB_ISSUE = "github_issue"
    GITHUB_PR = "github_pr"
    BOUNTY_CLAIM = "bounty_claim"
    BOUNTY_CHECK = "bounty_check"

    # PR lifecycle tasks
    PR_FOLLOWUP = "pr_followup"
    PR_CHANGE = "pr_change"
    PR_MERGE = "pr_merge"

    # Crypto tasks
    AIRDROP_CHECK = "airdrop_check"
    AIRDROP_CLAIM = "airdrop_claim"
    CRYPTO_RESEARCH = "crypto_research"

    # Job tasks (hourly only)
    JOB_APPLY = "job_apply"
    JOB_FOLLOWUP = "job_followup"

    # Research (5%)
    RESEARCH = "research"

    # System
    SYSTEM_CHECK = "system_check"
    DATA_REFRESH = "data_refresh"


@dataclass
class Task:
    """Represents a single task in the queue."""

    id: str
    type: str
    priority: int
    status: str
    data: dict
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(**data)


class TaskQueue:
    """Manages Andile's task execution queue."""

    # Priority order (lower = higher priority)
    PRIORITY_ORDER = {
        TaskType.PR_FOLLOWUP.value: 0,  # Highest - don't lose PRs!
        TaskType.PR_CHANGE.value: 0,  # Highest - don't get PRs closed
        TaskType.BOUNTY_CLAIM.value: 1,  # High - don't lose money
        TaskType.BOUNTY_CHECK.value: 1,  # High - check for bounties
        TaskType.PR_MERGE.value: 1,  # High - PR merged tasks
        TaskType.GITHUB_ISSUE.value: 1,  # High - new issues
        TaskType.GITHUB_PR.value: 1,  # High - PR tasks
        TaskType.AIRDROP_CHECK.value: 2,  # Medium
        TaskType.AIRDROP_CLAIM.value: 2,
        TaskType.CRYPTO_RESEARCH.value: 2,
        TaskType.JOB_APPLY.value: 2,  # Medium - hourly only
        TaskType.JOB_FOLLOWUP.value: 2,
        TaskType.RESEARCH.value: 3,  # Low
        TaskType.SYSTEM_CHECK.value: 4,  # Lowest
        TaskType.DATA_REFRESH.value: 4,
    }

    def __init__(self):
        self._lock = Lock()
        self._queue = self._load_queue()

    def _load_queue(self) -> dict:
        """Load queue from file."""
        if QUEUE_FILE.exists():
            try:
                with open(QUEUE_FILE, "r") as f:
                    return json.load(f)
            except:
                pass

        return {
            "tasks": [],
            "completed": [],
            "failed": [],
            "stats": {
                "total_created": 0,
                "total_completed": 0,
                "total_failed": 0,
                "last_task_time": None,
            },
        }

    def _save_queue(self):
        """Save queue to file."""
        QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(QUEUE_FILE, "w") as f:
            json.dump(self._queue, f, indent=2)

    def _generate_id(self) -> str:
        """Generate unique task ID."""
        return f"task_{int(time.time())}_{random.randint(1000, 9999)}"

    def add_task(
        self, task_type: str, data: dict, priority: int = None, max_attempts: int = 3
    ) -> str:
        """Add a new task to the queue.

        Args:
            task_type: Type of task (from TaskType)
            data: Task-specific data
            priority: Priority (1-5, lower = higher)
            max_attempts: Max retry attempts

        Returns:
            Task ID
        """
        if priority is None:
            priority = self.PRIORITY_ORDER.get(task_type, 3)

        task = Task(
            id=self._generate_id(),
            type=task_type,
            priority=priority,
            status=TaskStatus.PENDING.value,
            data=data,
            created_at=datetime.now().isoformat(),
            max_attempts=max_attempts,
        )

        with self._lock:
            self._queue["tasks"].append(task.to_dict())
            self._queue["stats"]["total_created"] += 1
            self._queue["stats"]["last_task_time"] = datetime.now().isoformat()
            self._save_queue()

        logger.info(f"Added task {task.id}: {task_type}")
        return task.id

    def get_next_task(self, job_hourly_only: bool = False) -> Optional[Task]:
        """Get the next task to execute.

        Args:
            job_hourly_only: If True, only return job tasks (for hourly trigger)

        Returns:
            Next task or None
        """
        with self._lock:
            # Sort by priority (lower = higher priority)
            pending = [
                t
                for t in self._queue["tasks"]
                if t["status"] == TaskStatus.PENDING.value
            ]
            pending.sort(key=lambda x: (x["priority"], x["created_at"]))

            # If job_hourly_only, only return job tasks
            if job_hourly_only:
                job_tasks = [
                    t
                    for t in pending
                    if t["type"]
                    in [TaskType.JOB_APPLY.value, TaskType.JOB_FOLLOWUP.value]
                ]
                if job_tasks:
                    task_dict = job_tasks[0]
                    self._update_task_status(
                        task_dict["id"], TaskStatus.IN_PROGRESS.value
                    )
                    return Task.from_dict(task_dict)
                return None

            # Otherwise return highest priority task
            if pending:
                task_dict = pending[0]
                self._update_task_status(task_dict["id"], TaskStatus.IN_PROGRESS.value)
                return Task.from_dict(task_dict)

            return None

    def _update_task_status(self, task_id: str, status: str):
        """Update task status."""
        for task in self._queue["tasks"]:
            if task["id"] == task_id:
                task["status"] = status
                if status == TaskStatus.IN_PROGRESS.value:
                    task["started_at"] = datetime.now().isoformat()
                    task["attempts"] += 1
                elif status == TaskStatus.COMPLETED.value:
                    task["completed_at"] = datetime.now().isoformat()
                    self._queue["stats"]["total_completed"] += 1
                elif status == TaskStatus.FAILED.value:
                    self._queue["stats"]["total_failed"] += 1
                break
        self._save_queue()

    def complete_task(self, task_id: str, result: dict = None):
        """Mark task as completed."""
        with self._lock:
            for task in self._queue["tasks"]:
                if task["id"] == task_id:
                    task["status"] = TaskStatus.COMPLETED.value
                    task["completed_at"] = datetime.now().isoformat()
                    if result:
                        task["result"] = result

                    # Move to completed
                    self._queue["completed"].append(task)
                    self._queue["tasks"].remove(task)
                    self._queue["stats"]["total_completed"] += 1
                    break
            self._save_queue()

    def fail_task(self, task_id: str, error: str):
        """Mark task as failed."""
        with self._lock:
            for task in self._queue["tasks"]:
                if task["id"] == task_id:
                    task["last_error"] = error

                    if task["attempts"] >= task["max_attempts"]:
                        # Max retries reached - move to failed
                        task["status"] = TaskStatus.FAILED.value
                        self._queue["failed"].append(task)
                        self._queue["tasks"].remove(task)
                        self._queue["stats"]["total_failed"] += 1
                        logger.error(f"Task {task_id} failed permanently: {error}")
                    else:
                        # Retry later
                        task["status"] = TaskStatus.PENDING.value
                        logger.warning(f"Task {task_id} failed, will retry: {error}")
                    break
            self._save_queue()

    def get_status(self) -> dict:
        """Get queue status."""
        with self._lock:
            pending = [
                t
                for t in self._queue["tasks"]
                if t["status"] == TaskStatus.PENDING.value
            ]
            in_progress = [
                t
                for t in self._queue["tasks"]
                if t["status"] == TaskStatus.IN_PROGRESS.value
            ]

            return {
                "pending": len(pending),
                "in_progress": len(in_progress),
                "completed_today": len(
                    [
                        t
                        for t in self._queue["completed"]
                        if (t.get("completed_at") or "").startswith(
                            datetime.now().date().isoformat()
                        )
                    ]
                ),
                "failed_today": len(
                    [
                        t
                        for t in self._queue["failed"]
                        if (t.get("completed_at") or "").startswith(
                            datetime.now().date().isoformat()
                        )
                    ]
                ),
                "stats": self._queue["stats"],
                "next_task": pending[0] if pending else None,
            }

    def get_pending_by_type(self, task_type: str) -> List[Task]:
        """Get all pending tasks of a specific type."""
        with self._lock:
            return [
                Task.from_dict(t)
                for t in self._queue["tasks"]
                if t["status"] == TaskStatus.PENDING.value and t["type"] == task_type
            ]

    def add_job_tasks(self, jobs: List[dict]):
        """Add job application tasks from job list."""
        for job in jobs:
            if not job.get("applied") and not job.get("application_sent"):
                self.add_task(
                    TaskType.JOB_APPLY.value,
                    {
                        "company": job.get("company"),
                        "title": job.get("title"),
                        "recipient": job.get("email"),
                        "url": job.get("url"),
                    },
                    priority=3,
                )

    def add_github_tasks(self, repos: List[dict]):
        """Add GitHub tasks from target repos."""
        for repo in repos:
            self.add_task(
                TaskType.GITHUB_ISSUE.value,
                {
                    "repo": repo.get("full_name"),
                    "label": repo.get("label", "bug"),
                    "priority": repo.get("priority", "medium"),
                },
                priority=1,
            )


# Singleton instance
_task_queue = None


def get_task_queue() -> TaskQueue:
    """Get the global task queue instance."""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue()
    return _task_queue
