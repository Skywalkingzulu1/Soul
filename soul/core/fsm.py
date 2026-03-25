from enum import Enum
from typing import List, Dict, Any, Optional
from soul.core.logger import setup_logger

logger = setup_logger(__name__)

# Maximum history entries to prevent memory bloat
MAX_HISTORY = 100


class State(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    REFLECTING = "reflecting"
    ERROR = "error"
    SUCCESS = "success"


class MissionFSM:
    """Finite State Machine for mission execution coherence."""

    def __init__(self, mission_name: str):
        self.mission_name = mission_name
        self.state = State.IDLE
        self.history: List[Dict[str, Any]] = []
        self.frustration_counter = 0
        self.max_frustration = 3

    def transition(self, to_state: State):
        logger.info(
            f"Mission {self.mission_name} transitioning: {self.state.value} -> {to_state.value}"
        )
        self.state = to_state

    def log_action(self, action: str, result: Any):
        # Frustration Monitoring: Detect loops
        if self.history and self.history[-1]["action"] == action:
            self.frustration_counter += 1
            logger.warning(
                f"Repeated action detected: {action}. Frustration: {self.frustration_counter}"
            )
        else:
            self.frustration_counter = 0

        self.history.append({"action": action, "result": result})

        # Bounded history to prevent memory bloat
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]
            logger.debug(f"History truncated to {MAX_HISTORY} entries")

        if self.frustration_counter >= self.max_frustration:
            logger.error(
                f"Mission {self.mission_name} aborted due to infinite loop frustration."
            )
            self.transition(State.ERROR)
            return False
        return True

    def get_summary(self):
        return {
            "mission": self.mission_name,
            "state": self.state.value,
            "steps": len(self.history),
            "frustration": self.frustration_counter,
            "max_history": MAX_HISTORY,
        }

    def clear_history(self):
        """Clear history to free memory."""
        cleared = len(self.history)
        self.history = []
        logger.info(f"Cleared {cleared} history entries")
        return cleared
