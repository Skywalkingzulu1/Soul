import json
import os
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "system_state.json")

class StateMachine:
    """Deterministic state tracker for the Digital Twin."""
    
    STATES = ["IDLE", "RESEARCHING", "EXECUTING", "SLEEPING", "ERROR"]

    def __init__(self) -> None:
        self.data = {}
        self.load()

    def load(self) -> None:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = self._default_state()
        else:
            self.data = self._default_state()
            self.save()

    def _default_state(self) -> None:
        return {
            "current_state": "IDLE",
            "last_action": "System Initialized",
            "last_update": time.time(),
            "active_tool": None,
            "task_queue_depth": 0
        }

    def save(self) -> None:
        self.data["last_update"] = time.time()
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")

    def update(self, state=None, action=None, tool=None, clear_tool=False) -> None:
        if state and state in self.STATES:
            self.data["current_state"] = state
        if action:
            self.data["last_action"] = action
        if tool:
            self.data["active_tool"] = tool
        if clear_tool:
            self.data["active_tool"] = None
        self.save()

    def get_summary(self) -> None:
        return (
            f"STATE: {self.data['current_state']}\n"
            f"LAST ACTION: {self.data['last_action']}\n"
            f"ACTIVE TOOL: {self.data['active_tool'] or 'None'}"
        )

# Global singleton
state_machine = StateMachine()
