"""Time awareness for Andile Sizophila."""

import time
import datetime


class Clock:
    """Provides time awareness — the soul knows what time it is and how long things take."""

    def __init__(self) -> None:
        self.start_time = time.time()
        self.session_start = datetime.datetime.now()

    def now(self) -> None:
        return datetime.datetime.now()

    def timestamp(self) -> None:
        return time.time()

    def session_duration(self) -> None:
        """How long the soul has been awake this session."""
        elapsed = time.time() - self.start_time
        if elapsed < 60:
            return f"{elapsed:.0f} seconds"
        elif elapsed < 3600:
            return f"{elapsed / 60:.1f} minutes"
        else:
            return f"{elapsed / 3600:.1f} hours"

    def time_of_day(self) -> None:
        hour = self.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    def format_now(self) -> None:
        return self.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_context(self) -> None:
        """Return a time context string for prompts."""
        return (
            f"Current time: {self.format_now()} ({self.time_of_day()})\n"
            f"Session duration: {self.session_duration()}"
        )

    def elapsed_since(self, past_timestamp) -> None:
        """How long since a past timestamp."""
        elapsed = time.time() - past_timestamp
        if elapsed < 60:
            return f"{elapsed:.1f}s"
        elif elapsed < 3600:
            return f"{elapsed / 60:.1f}m"
        else:
            return f"{elapsed / 3600:.1f}h"
