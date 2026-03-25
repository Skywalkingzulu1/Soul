"""
Brain Orchestrator — connects all 216 modules via Global Workspace Theory.

Architecture:
  Input → Thalamic Gateway → Lazy-Load Relevant Modules → Sequential Processing → Competition → Broadcast → Output

Modules are loaded ONLY when their category is needed. Sequential processing avoids memory spikes.
"""

import importlib
import logging
import time

from soul.base_module import BrainModule

logger = logging.getLogger(__name__)

MODULE_DIRS = [
    "executive_core",
    "language_core",
    "perception_core",
    "attention_core",
    "integration_core",
    "knowledge_core",
    "reading_core",
    "social_core",
    "vision_core",
    "memory_core",
    "emotion_core",
    "reward_core",
    "mood_core",
    "arousal_core",
    "homeostasis_core",
    "habit_core",
    "coordination_core",
    "vital_core",
    "relay_core",
    "spatial_core",
]

# Map category names to directory names
CATEGORY_TO_DIR = {d.replace("_core", ""): d for d in MODULE_DIRS}


class GlobalWorkspace:
    """Global Workspace — central competition/broadcast mechanism."""

    def __init__(self) -> None:
        self.contents = []
        self.max_contents = 7
        self.broadcast_history = []

    def compete(self, module_results) -> None:
        scored = []
        for result in module_results:
            if result and result.get("confidence", 0) > 0:
                score = result["confidence"]
                if result.get("state", {}).get("activation", 0) > 0.7:
                    score *= 1.5
                scored.append((score, result))
        scored.sort(key=lambda x: x[0], reverse=True)
        winners = [s[1] for s in scored[: self.max_contents]]
        self.contents = winners
        return winners

    def broadcast(self, winners) -> None:
        broadcast = {
            "timestamp": time.time(),
            "winners": winners,
            "summary": self._summarize(winners),
        }
        self.broadcast_history.append(broadcast)
        if len(self.broadcast_history) > 50:
            self.broadcast_history = self.broadcast_history[-25:]
        return broadcast

    def _summarize(self, winners) -> None:
        if not winners:
            return "No active modules"
        areas = set(w.get("area", "?") for w in winners)
        return f"Active: {', '.join(list(areas)[:5])}"


class ThalamicGateway:
    """Routes input to appropriate module categories."""

    ROUTING = {
        "question": ["executive", "language", "knowledge"],
        "command": ["executive", "habit", "coordination"],
        "emotion": ["emotion", "mood", "reward"],
        "visual": ["vision", "perception", "attention"],
        "memory": ["memory", "knowledge", "integration"],
        "social": ["social", "emotion", "language"],
        "action": ["executive", "habit", "vital"],
        "default": ["executive", "language", "attention"],
    }

    def route(self, input_text) -> None:
        text = input_text.lower() if isinstance(input_text, str) else ""
        if any(
            w in text
            for w in ["feel", "emotion", "happy", "sad", "angry", "frustrated"]
        ):
            return self.ROUTING["emotion"]
        if any(w in text for w in ["see", "look", "image", "color"]):
            return self.ROUTING["visual"]
        if any(w in text for w in ["remember", "recall", "forgot"]):
            return self.ROUTING["memory"]
        if any(w in text for w in ["do", "run", "execute", "send", "create"]):
            return self.ROUTING["action"]
        if any(w in text for w in ["who", "what", "where", "when", "why", "how"]):
            return self.ROUTING["question"]
        return self.ROUTING["default"]


class BrainOrchestrator:
    """Orchestrates all 216 brain modules. Lazy-loaded, sequential processing."""

    def __init__(self) -> None:
        self.workspace = GlobalWorkspace()
        self.gateway = ThalamicGateway()
        self.modules = {}
        self._loaded_categories = set()

    def _load_category(self, category) -> None:
        """Load modules for a specific category only when needed."""
        if category in self._loaded_categories:
            return
        self._loaded_categories.add(category)

        dir_name = CATEGORY_TO_DIR.get(category)
        if not dir_name:
            return

        loaded = 0
        try:
            mod = importlib.import_module(f"soul.{dir_name}")
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BrainModule)
                    and attr is not BrainModule
                ):
                    try:
                        instance = attr()
                        if instance.name not in self.modules:
                            self.modules[instance.name] = instance
                            loaded += 1
                    except Exception:
                        pass
        except ImportError:
            pass

        if loaded > 0:
            logger.debug(f"Loaded {loaded} modules for {category}")

    def process(self, input_data, context=None) -> None:
        """Process input through the brain pipeline. Sequential to save memory."""
        text = (
            input_data.get("text", "")
            if isinstance(input_data, dict)
            else str(input_data)
        )

        # 1. Route
        categories = self.gateway.route(text)

        # 2. Lazy-load needed categories
        for cat in categories:
            self._load_category(cat)

        # 3. Select relevant modules (sequential)
        active_modules = []
        for name, module in self.modules.items():
            for cat in categories:
                if cat in name or cat in module.brain_area.lower():
                    active_modules.append(module)
                    break

        # 4. Sequential processing (no ThreadPoolExecutor to save memory)
        results = []
        for m in active_modules[:10]:  # Limit to 10 modules per query
            try:
                result = m.process(input_data, context)
                if result:
                    results.append(result)
            except Exception:
                pass

        # 5. Competition
        winners = self.workspace.compete(results)

        # 6. Broadcast
        broadcast = self.workspace.broadcast(winners)

        return {
            "input": text[:100],
            "categories": categories,
            "modules_active": len(active_modules),
            "modules_responded": len(results),
            "winners": winners,
            "broadcast": broadcast,
            "total_modules": len(self.modules),
        }

    def get_all_states(self) -> None:
        return {name: m.get_state() for name, m in self.modules.items()}

    def get_active_modules(self) -> None:
        return {
            name: m.get_state() for name, m in self.modules.items() if m.activation > 0
        }

    def get_stats(self) -> None:
        total = len(self.modules)
        active = sum(1 for m in self.modules.values() if m.activation > 0)
        total_calls = sum(m.call_count for m in self.modules.values())
        return {
            "total_modules": total,
            "active_modules": active,
            "total_calls": total_calls,
            "categories_loaded": len(self._loaded_categories),
            "workspace_contents": len(self.workspace.contents),
            "broadcasts": len(self.workspace.broadcast_history),
        }
