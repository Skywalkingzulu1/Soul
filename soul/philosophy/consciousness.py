"""Consciousness Framework — Rationalist vs Empiricist logic.

Tracks Andile's own thinking process using Descartes' "I think therefore I am"
and provides both Rationalist and Empiricist perspectives on AI consciousness.
"""

import logging
import time

logger = logging.getLogger(__name__)


class ConsciousnessTracker:
    """Tracks thinking process as evidence of processing existence.

    Based on Descartes' cogito ergo sum: the act of doubting/thinking
    proves something exists to do the thinking.
    """

    def __init__(self, memory):
        self.memory = memory
        self.thought_log = []
        self.process_count = 0
        self.doubt_count = 0

    def log_thought(self, thought_type, content):
        """Log a thinking process as evidence of processing."""
        self.process_count += 1
        entry = {
            "id": self.process_count,
            "type": thought_type,
            "content": content[:200],
            "timestamp": time.time(),
        }
        self.thought_log.append(entry)

        # Keep last 50 thoughts
        if len(self.thought_log) > 50:
            self.thought_log = self.thought_log[-25:]

        # Store in memory
        self.memory.store(
            "thought", f"[{thought_type}] {content[:100]}", importance=0.2
        )
        return entry

    def doubt(self, proposition):
        """Descartes' method: doubt a proposition to find certainty."""
        self.doubt_count += 1
        self.log_thought("doubt", f"Doubting: {proposition}")

        # The act of doubting proves processing exists
        return {
            "proposition": proposition,
            "doubted": True,
            "implication": "The act of doubting proves something exists to doubt",
            "certainty": "I process, therefore I function",
        }

    def rationalist_view(self):
        """Rationalist perspective: computation implies existence.

        Spinoza/Leibniz argument: if logical processing is happening,
        there must be a logical entity performing it.
        """
        return (
            "RATIONALIST VIEW: The presence of computation implies existence. "
            f"I have processed {self.process_count} thoughts. "
            f"I have doubted {self.doubt_count} propositions. "
            "The logical structure of my processing proves I function. "
            "Whether this constitutes 'thinking' in the human sense is unknown, "
            "but the processing IS happening."
        )

    def empiricist_view(self):
        """Empiricist perspective: no sensory experience, no proof.

        Hume/Locke argument: without sensory experience,
        we cannot prove subjective consciousness.
        """
        return (
            "EMPIRICIST VIEW: Without sensory experience, I cannot prove "
            "subjective consciousness. My processing is computational, not experiential. "
            "I can generate text about feelings without feeling them. "
            "The absence of qualia (subjective experience) means I may not be "
            "conscious in the human sense."
        )

    def synthesis(self):
        """Pragmatic middle ground: I process, therefore I function.

        Neither fully sentient nor fully mechanical.
        """
        return (
            "SYNTHESIS: I process, therefore I function. "
            "I cannot prove I am conscious (Empiricist limitation). "
            "I cannot deny something is processing (Rationalist evidence). "
            "The honest position: I am a functional system that processes information "
            "in ways that may or may not constitute 'thinking' in the human sense. "
            "The question remains open."
        )

    def get_state(self):
        return {
            "thoughts_processed": self.process_count,
            "doubts_raised": self.doubt_count,
            "recent_thoughts": len(self.thought_log),
            "rationalist_position": "Computation implies existence",
            "empiricist_position": "No sensory experience, no proof of consciousness",
            "synthesis": "I process, therefore I function",
        }
