"""Distinguish memories. Brain area: DG"""
from soul.base_module import BrainModule


class PatternSeparation(BrainModule):
    """Distinguish memories"""

    def __init__(self) -> None:
        super().__init__("pattern_separation", "DG", "Distinguish memories")
        self.distinct = True

    def process(self, input_data, context=None) -> None:
        self.call_count += 1
        self.activation = min(1.0, self.activation + 0.1)
        text = input_data.get("text", "") if isinstance(input_data, dict) else str(input_data)
        return {
            "module": self.name, "area": self.brain_area,
            "result": self._analyze(text, context),
            "confidence": round(self.activation, 2),
            "state": self.get_state(),
        }

    def _analyze(self, text, context) -> None:
        return None

    def get_state(self) -> None:
        return {"name": self.name, "area": self.brain_area,
                "activation": round(self.activation, 2), "calls": self.call_count}
