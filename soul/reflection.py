import logging

logger = logging.getLogger(__name__)

from soul.ollama_client import generate

REFLECT_PROMPT = (
    "You are reflecting on your own performance. Be brutally honest.\n\n"
    "INPUT RECEIVED: {input_text}\n"
    "YOUR RESPONSE: {response}\n\n"
    "CRITICAL: Answer ALL 4 questions below COMPLETELY. Do not cut any short.\n\n"
    "1. What did I do well?\n"
    "2. What mistakes did I make?\n"
    "3. What should I do differently next time?\n"
    "4. What did I learn?\n\n"
    "REFLECTION (answer all questions fully):"
)

META_REFLECT_PROMPT = (
    "Look at these past reflections and identify patterns.\n\n"
    "PAST REFLECTIONS:\n{reflections}\n\n"
    "What recurring themes do you see?\n"
    "What should you change about HOW you think?\n\n"
    "META-REFLECTION:"
)


class Reflector:
    """Self-reflection engine. The soul learns from every interaction."""

    def __init__(self, memory) -> None:
        self.memory = memory

    def reflect(self, input_text, response) -> None:
        prompt = REFLECT_PROMPT.format(input_text=input_text, response=response)
        try:
            result = generate(
                prompt=prompt,
                temperature=0.5,
                num_predict=800,
            )
            reflection = result["response"]

            # Store reflection as memory
            self.memory.store("reflection", reflection, importance=0.7)
            logger.info("Reflection stored.")
            return reflection
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            return None

    def meta_reflect(self) -> None:
        """Reflect on patterns across past reflections."""
        past = self.memory.recall("reflection patterns learning", n=5)
        if not past:
            return None

        reflections_text = "\n---\n".join(past)
        prompt = META_REFLECT_PROMPT.format(reflections=reflections_text)

        try:
            result = generate(
                prompt=prompt,
                temperature=0.5,
                num_predict=600,
            )
            meta = result["response"]
            self.memory.store("meta_reflection", meta, importance=0.9)
            logger.info("Meta-reflection stored.")
            return meta
        except Exception as e:
            logger.error(f"Meta-reflection failed: {e}")
            return None
