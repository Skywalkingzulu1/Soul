"""
Base module for all 180 brain modules. Lightweight by design.
Each module: process(input, context) -> output dict
"""


class BrainModule:
    """Base class for all brain modules. Minimal memory footprint."""

    def __init__(self, name, brain_area, description=""):
        self.name = name
        self.brain_area = brain_area
        self.description = description
        self.state = {}
        self.activation = 0.0  # 0.0 = dormant, 1.0 = fully active
        self.call_count = 0

    def process(self, input_data, context=None):
        """Process input and return output. Override in subclasses."""
        self.call_count += 1
        self.activation = min(1.0, self.activation + 0.1)
        return {"module": self.name, "result": None, "confidence": 0.5}

    def get_state(self):
        return {
            "name": self.name,
            "area": self.brain_area,
            "activation": self.activation,
            "calls": self.call_count,
        }

    def update(self, feedback):
        """Learn from feedback."""
        if feedback.get("success"):
            self.activation = min(1.0, self.activation + 0.05)
        else:
            self.activation = max(0.0, self.activation - 0.05)

    def reset(self):
        self.activation = 0.0
