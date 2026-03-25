"""Error distribution. Brain area: IO"""
from soul.base_module import BrainModule


class ErrorRelay(BrainModule):
    """Error distribution"""

    def __init__(self):
        super().__init__("error_relay", "IO", "Error distribution")
        self.error_relay = True

    def process(self, input_data, context=None):
        self.call_count += 1
        self.activation = min(1.0, self.activation + 0.1)
        text = input_data.get("text", "") if isinstance(input_data, dict) else str(input_data)
        return {
            "module": self.name, "area": self.brain_area,
            "result": self._analyze(text, context),
            "confidence": round(self.activation, 2),
            "state": self.get_state(),
        }

    def _analyze(self, text, context):
        return None

    def get_state(self):
        return {"name": self.name, "area": self.brain_area,
                "activation": round(self.activation, 2), "calls": self.call_count}
