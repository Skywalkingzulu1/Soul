"""GitHub Comment Rate Limiter

Limits GitHub comments to prevent spam:
- Max 5 comments per hour
- Max 20 comments per day
- Max 1 comment per PR per hour
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock

from soul.core.logger import setup_logger

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATS_FILE = BASE_DIR / "knowledge" / "github_stats.json"


class GitHubRateLimiter:
    """Rate limiter for GitHub comments."""

    MAX_DAILY = 20
    MAX_HOURLY = 5
    MAX_PER_PR_HOUR = 1

    def __init__(self):
        self._lock = Lock()
        self._stats = self._load_stats()
        self._check_and_reset_daily()
        self._check_and_reset_hourly()

    def _load_stats(self) -> dict:
        """Load GitHub statistics from file."""
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE, "r") as f:
                    return json.load(f)
            except:
                pass

        return {
            "sent_today": 0,
            "last_reset_date": datetime.now().date().isoformat(),
            "hourly": {},
            "by_pr": {},
            "last_reset_hour": datetime.now().hour,
            "total_sent": 0,
            "successful": 0,
            "failed": 0,
            "last_sent": None,
        }

    def _save_stats(self):
        """Save GitHub statistics to file."""
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATS_FILE, "w") as f:
            json.dump(self._stats, f, indent=2)

    def _check_and_reset_daily(self):
        """Reset daily counters if it's a new day."""
        today = datetime.now().date().isoformat()
        if self._stats.get("last_reset_date") != today:
            logger.info(f"New day detected - resetting daily GitHub comment counter")
            self._stats["sent_today"] = 0
            self._stats["hourly"] = {}
            self._stats["by_pr"] = {}
            self._stats["last_reset_date"] = today
            self._save_stats()

    def _check_and_reset_hourly(self):
        """Reset hourly counter if it's a new hour."""
        current_hour = datetime.now().hour
        if self._stats.get("last_reset_hour") != current_hour:
            self._stats["last_reset_hour"] = current_hour
            self._save_stats()

    def can_comment(self, pr_id: str = None) -> tuple[bool, str]:
        """Check if we can post a comment.

        Returns:
            (can_comment, reason)
        """
        with self._lock:
            self._check_and_reset_daily()
            self._check_and_reset_hourly()

            # Check daily limit
            if self._stats["sent_today"] >= self.MAX_DAILY:
                return False, f"Daily limit reached ({self.MAX_DAILY})"

            # Check hourly limit
            current_hour = str(datetime.now().hour)
            hourly_sent = self._stats["hourly"].get(current_hour, 0)
            if hourly_sent >= self.MAX_HOURLY:
                return False, f"Hourly limit reached ({self.MAX_HOURLY})"

            # Check per-PR limit
            if pr_id:
                pr_key = pr_id.lower()
                sent_to_pr = self._stats["by_pr"].get(pr_key, 0)
                if sent_to_pr >= self.MAX_PER_PR_HOUR:
                    return False, f"PR limit reached for {pr_id}"

            return True, "OK"

    def record_comment(self, pr_id: str = None):
        """Record a successful comment."""
        with self._lock:
            now = datetime.now()

            self._stats["sent_today"] += 1
            self._stats["total_sent"] += 1
            self._stats["successful"] += 1
            self._stats["last_sent"] = now.isoformat()

            # Update hourly
            hour_key = str(now.hour)
            self._stats["hourly"][hour_key] = self._stats["hourly"].get(hour_key, 0) + 1

            # Update per-PR
            if pr_id:
                pr_key = pr_id.lower()
                self._stats["by_pr"][pr_key] = self._stats["by_pr"].get(pr_key, 0) + 1

            self._save_stats()

            logger.info(
                f"GitHub comment recorded. Today: {self._stats['sent_today']}/{self.MAX_DAILY}"
            )

    def get_status(self) -> dict:
        """Get current rate limiter status."""
        with self._lock:
            self._check_and_reset_daily()
            self._check_and_reset_hourly()

            current_hour = str(datetime.now().hour)
            hourly_sent = self._stats["hourly"].get(current_hour, 0)

            return {
                "can_comment": self._stats["sent_today"] < self.MAX_DAILY
                and hourly_sent < self.MAX_HOURLY,
                "daily": {
                    "sent": self._stats["sent_today"],
                    "limit": self.MAX_DAILY,
                    "remaining": self.MAX_DAILY - self._stats["sent_today"],
                    "percentage": round(
                        self._stats["sent_today"] / self.MAX_DAILY * 100, 1
                    ),
                },
                "hourly": {
                    "sent": hourly_sent,
                    "limit": self.MAX_HOURLY,
                    "remaining": self.MAX_HOURLY - hourly_sent,
                },
                "total": {
                    "sent": self._stats.get("total_sent", 0),
                    "successful": self._stats.get("successful", 0),
                    "failed": self._stats.get("failed", 0),
                },
                "last_sent": self._stats.get("last_sent"),
            }


# Singleton instance
_github_rate_limiter = None


def get_github_rate_limiter() -> GitHubRateLimiter:
    """Get the global GitHub rate limiter instance."""
    global _github_rate_limiter
    if _github_rate_limiter is None:
        _github_rate_limiter = GitHubRateLimiter()
    return _github_rate_limiter
