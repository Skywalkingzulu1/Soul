"""Calendar Planning System - 4-Hour Macro Cycle

Instead of a 1-2 hour cycle, Andile executes in 4-hour blocks:

4-HOUR MACRO CYCLE
├─ BLOCK 1: GITHUB WORK (60 mins)
│  ├─ 40 mins: High priority coding (fix issues, create PRs)
│  └─ 20 mins: Low priority (research issues, check PR status)
│
├─ BLOCK 2: JOB SEARCH (60 mins)
│  ├─ 40 mins: Research companies, tailor CVs
│  └─ 20 mins: Apply to jobs (max 5)
│
├─ BLOCK 3: CRYPTO WORK (60 mins)
│  ├─ 40 mins: Check airdrops, scan bounties
│  └─ 20 mins: Claim/process crypto tasks
│
├─ BLOCK 4: MAINTENANCE (60 mins)
│  ├─ 20 mins: System health checks
│  ├─ 20 mins: Research/learning
│  └─ 20 mins: Hourly report generation
│
└─ REPEAT: 6 cycles per day (24 hours)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from threading import Lock

from soul.core.logger import setup_logger

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CALENDAR_FILE = BASE_DIR / "knowledge" / "calendar.json"


class CalendarPlanner:
    """Maps out Andile's 4-hour macro execution cycle."""

    # 4-Hour Macro Cycle Configuration
    MACRO_CYCLE = {
        "duration_hours": 4,
        "blocks": [
            {
                "id": "github",
                "name": "GitHub Work",
                "duration_minutes": 60,
                "tasks": [
                    {
                        "type": "github_coding",
                        "duration_minutes": 40,
                        "priority": "high",
                    },
                    {
                        "type": "github_research",
                        "duration_minutes": 20,
                        "priority": "low",
                    },
                ],
            },
            {
                "id": "jobs",
                "name": "Job Search",
                "duration_minutes": 60,
                "tasks": [
                    {
                        "type": "job_research",
                        "duration_minutes": 40,
                        "priority": "high",
                    },
                    {"type": "job_apply", "duration_minutes": 20, "priority": "low"},
                ],
            },
            {
                "id": "crypto",
                "name": "Crypto Work",
                "duration_minutes": 60,
                "tasks": [
                    {"type": "crypto_scan", "duration_minutes": 40, "priority": "high"},
                    {"type": "crypto_claim", "duration_minutes": 20, "priority": "low"},
                ],
            },
            {
                "id": "maintenance",
                "name": "Maintenance",
                "duration_minutes": 60,
                "tasks": [
                    {
                        "type": "system_check",
                        "duration_minutes": 20,
                        "priority": "high",
                    },
                    {"type": "research", "duration_minutes": 20, "priority": "medium"},
                    {"type": "report", "duration_minutes": 20, "priority": "low"},
                ],
            },
        ],
    }

    def __init__(self):
        self._lock = Lock()
        self.calendar = self._load_calendar()
        self.cycle_start_time = datetime.now()
        self.current_cycle = 0
        self.current_block_index = 0
        self.block_start_time = datetime.now()

    def _load_calendar(self) -> dict:
        """Load calendar from file."""
        if CALENDAR_FILE.exists():
            try:
                with open(CALENDAR_FILE, "r") as f:
                    return json.load(f)
            except:
                pass

        return {
            "macro_cycle": self.MACRO_CYCLE,
            "current_cycle": 0,
            "current_block": None,
            "cycle_start": None,
            "block_start": None,
            "planned_tasks": {},
            "completed_tasks": {},
            "stats": {
                "total_cycles": 0,
                "total_blocks": 0,
                "total_planned": 0,
                "total_completed": 0,
            },
        }

    def _save_calendar(self):
        """Save calendar to file."""
        CALENDAR_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CALENDAR_FILE, "w") as f:
            json.dump(self.calendar, f, indent=2)

    def get_current_block(self) -> dict:
        """Get the current active block."""
        blocks = self.MACRO_CYCLE["blocks"]

        # Calculate which block we're in based on elapsed time
        now = datetime.now()
        elapsed = now - self.cycle_start_time
        elapsed_minutes = elapsed.total_seconds() / 60

        # Determine block
        cumulative = 0
        for i, block in enumerate(blocks):
            cumulative += block["duration_minutes"]
            if elapsed_minutes < cumulative:
                return {
                    "index": i,
                    "block": block,
                    "time_in_block": elapsed_minutes
                    - (cumulative - block["duration_minutes"]),
                    "time_remaining": cumulative - elapsed_minutes,
                }

        # If past all blocks, cycle is complete
        return None

    def get_current_task_type(self) -> str:
        """Get the current task type based on time within block."""
        block_info = self.get_current_block()
        if not block_info:
            return None

        block = block_info["block"]
        time_in_block = block_info["time_in_block"]

        # Determine which task within the block
        cumulative = 0
        for task in block["tasks"]:
            cumulative += task["duration_minutes"]
            if time_in_block < cumulative:
                return task["type"]

        return block["tasks"][-1]["type"]

    def is_new_cycle_needed(self) -> bool:
        """Check if a new macro cycle should start."""
        now = datetime.now()
        elapsed = now - self.cycle_start_time
        cycle_duration = timedelta(hours=self.MACRO_CYCLE["duration_hours"])
        return elapsed >= cycle_duration

    def start_new_cycle(self) -> int:
        """Start a new 4-hour macro cycle."""
        self.current_cycle += 1
        self.cycle_start_time = datetime.now()
        self.current_block_index = 0
        self.block_start_time = datetime.now()

        with self._lock:
            self.calendar["current_cycle"] = self.current_cycle
            self.calendar["cycle_start"] = self.cycle_start_time.isoformat()
            self.calendar["stats"]["total_cycles"] = self.current_cycle
            self._save_calendar()

        logger.info(f"=== STARTING MACRO CYCLE {self.current_cycle} ===")
        return self.current_cycle

    def get_cycle_config(self) -> dict:
        """Get the current cycle configuration."""
        return self.MACRO_CYCLE

    def get_tasks_for_cycle(self) -> Dict[str, int]:
        """Get task counts for the current cycle."""
        return {
            "github_coding": 40,  # 40 mins worth of tasks
            "github_research": 20,  # 20 mins worth of tasks
            "job_research": 40,
            "job_apply": 20,
            "crypto_scan": 40,
            "crypto_claim": 20,
            "system_check": 20,
            "research": 20,
            "report": 20,
        }

    def plan_cycle_tasks(self, task_queue) -> List[dict]:
        """Plan tasks for the current cycle based on block timing."""
        today = datetime.now().date().isoformat()
        cycle_id = f"cycle_{self.current_cycle}_{today}"
        planned_tasks = []

        with self._lock:
            # Clear old planned tasks for today
            if today not in self.calendar.get("planned_tasks", {}):
                self.calendar["planned_tasks"][today] = []

            # Plan tasks for each block
            for block in self.MACRO_CYCLE["blocks"]:
                for task in block["tasks"]:
                    task_data = {
                        "id": f"{cycle_id}_{block['id']}_{task['type']}",
                        "type": task["type"],
                        "block": block["id"],
                        "cycle": self.current_cycle,
                        "duration_minutes": task["duration_minutes"],
                        "priority": task["priority"],
                        "status": "planned",
                        "created_at": datetime.now().isoformat(),
                    }
                    planned_tasks.append(task_data)
                    self.calendar["planned_tasks"][today].append(task_data)

            self.calendar["stats"]["total_planned"] = len(
                self.calendar["planned_tasks"].get(today, [])
            )
            self._save_calendar()

        logger.info(
            f"Planned {len(planned_tasks)} tasks for cycle {self.current_cycle}"
        )
        return planned_tasks

    def mark_task_completed(self, task_id: str):
        """Mark a planned task as completed."""
        today = datetime.now().date().isoformat()

        with self._lock:
            planned = self.calendar.get("planned_tasks", {}).get(today, [])
            for task in planned:
                if task.get("id") == task_id:
                    task["status"] = "completed"
                    task["completed_at"] = datetime.now().isoformat()

                    # Add to completed
                    if today not in self.calendar.get("completed_tasks", {}):
                        self.calendar["completed_tasks"][today] = []
                    self.calendar["completed_tasks"][today].append(task)

                    # Update stats
                    self.calendar["stats"]["total_completed"] += 1
                    break

            self._save_calendar()

    def get_daily_summary(self) -> dict:
        """Get summary of today's planned vs completed tasks."""
        today = datetime.now().date().isoformat()

        planned = self.calendar.get("planned_tasks", {}).get(today, [])
        completed = self.calendar.get("completed_tasks", {}).get(today, [])

        by_type = {}
        for task in planned:
            task_type = task.get("type", "unknown")
            if task_type not in by_type:
                by_type[task_type] = {"planned": 0, "completed": 0}
            by_type[task_type]["planned"] += 1

        for task in completed:
            task_type = task.get("type", "unknown")
            if task_type in by_type:
                by_type[task_type]["completed"] += 1

        completion_rate = 0
        if planned:
            completion_rate = round(len(completed) / len(planned) * 100, 1)

        current_block = self.get_current_block()

        return {
            "date": today,
            "current_cycle": self.current_cycle,
            "current_block": current_block["block"]["name"]
            if current_block
            else "None",
            "cycle_start": self.cycle_start_time.isoformat(),
            "total_planned": len(planned),
            "total_completed": len(completed),
            "completion_rate": completion_rate,
            "by_type": by_type,
            "config": self.MACRO_CYCLE,
        }

    def get_schedule_display(self) -> str:
        """Get human-readable schedule display."""
        config = self.MACRO_CYCLE
        blocks = config["blocks"]

        lines = [
            f"=== 4-HOUR MACRO CYCLE ===",
            f"Cycle Duration: {config['duration_hours']} hours",
            f"Current Cycle: {self.current_cycle}",
            "",
            "Blocks:",
        ]

        for block in blocks:
            lines.append(f"  {block['name']} ({block['duration_minutes']} mins):")
            for task in block["tasks"]:
                lines.append(
                    f"    - {task['type']} ({task['duration_minutes']} mins, {task['priority']})"
                )
            lines.append("")

        return "\n".join(lines)


# Singleton instance
_calendar_planner = None


def get_calendar_planner() -> CalendarPlanner:
    """Get the global calendar planner instance."""
    global _calendar_planner
    if _calendar_planner is None:
        _calendar_planner = CalendarPlanner()
    return _calendar_planner
