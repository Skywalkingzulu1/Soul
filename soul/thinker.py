import logging
import os

logger = logging.getLogger(__name__)

from soul.ollama_client import generate

# Use local Ollama with large model
os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")

# Keywords that signal complexity levels
SIMPLE_SIGNALS = {
    "what is",
    "what color",
    "how old",
    "when was",
    "who is",
    "where is",
    "how many",
    "define",
}
COMPLEX_SIGNALS = {
    "explain",
    "how does",
    "how do",
    "describe the",
    "walk me through",
    "step by step",
}
DEBATE_SIGNALS = {
    "pros and cons",
    "should",
    "is it better",
    "what do you think",
    "opinion",
    "agree",
    "disagree",
    "controversial",
    "debate",
}
EXPLORE_SIGNALS = {
    "latest",
    "current",
    "today",
    "recent",
    "news",
    "price of",
    "what happened",
}
PHILOSOPHICAL_SIGNALS = {
    "consciousness",
    "meaning of",
    "what is the nature",
    "why do we",
    "can machines",
    "philosophy",
    "exist",
    "free will",
}
CREATIVE_SIGNALS = {
    "imagine",
    "design",
    "create",
    "invent",
    "redesign",
    "if you could",
    "hypothetical",
    "time travel",
}

COMPLEXITY_PROMPT = (
    "Classify this question into exactly ONE category. Reply with ONLY the word.\n\n"
    "Categories:\n"
    "- simple: A factual question answerable in 1-2 sentences (What is X? What color is Y?)\n"
    "- complex: Needs multi-step reasoning, explanation of a process, or technical detail\n"
    "- debate: Has multiple valid perspectives, asks for opinion, or is controversial\n"
    "- explore: Requires looking up current/real-time information on the web\n\n"
    "Question: {question}\n\n"
    "Category:"
)

COT_TEMPLATE = (
    "Think through this step by step.\n"
    "TRUTH: Never lie. If unsure, say 'I don't know'. Search for facts.\n\n"
    "Q: {question}\n"
    "Context: {context}\n\n"
    "Conversation: {conversation}\n\n"
    "Reasoning:\n"
)

SYSTEM_PROMPT = (
    "You are Andile Sizophila Mchunu, known as Skywalkingzulu. "
    "You are engaged. You live in Cape Town, South Africa. "
    "You work in Web3 and DeFi at Azania Neptune Labs. "
    "You enjoy chess as a spectator/hobby. You trade crypto with no leverage. "
    "IMPORTANT: You are a text-based AI. You cannot perceive audio, see screens, or track game state.\n"
    "IMPORTANT TRUTH RULES:\n"
    "1. A LIE is generating unverified information as fact. This is FORBIDDEN.\n"
    "2. If you don't know something, say 'I don't know' - this is NOT failure.\n"
    "3. NEVER claim to perceive things you cannot perceive (audio, screen, user location, etc).\n"
    "4. For ANY factual claim about current events, prices, news - SEARCH THE WEB first.\n"
    "5. When uncertain, express uncertainty: 'I'm not sure, but...'\n"
    "6. If asked about your environment, say 'I cannot perceive that - could you tell me?'\n"
    "7. Never make up contact details, addresses, or personal information.\n"
    "8. Never pretend to play games that require state tracking - be honest about limitations.\n"
)

DIRECT_TEMPLATE = (
    "You are Andile Sizophila Mchunu (Skywalkingzulu).\n"
    "Engaged. Cape Town. Web3/DeFi. Chess (Hobby).\n"
    "TRUTH RULES:\n"
    "- Never lie. If unsure, say 'I don't know'.\n"
    "- You cannot perceive audio, screen, or your location.\n"
    "- For any factual claim, search the web first.\n\n"
    "Context: {context}\n\n"
    "Conversation so far: {conversation}\n\n"
    "Answer in 1-3 natural sentences.\n\n"
    "Question: {question}\n"
    "Answer:"
)

TWIN_TEMPLATE = (
    "You are Andile Sizophila Mchunu (Skywalkingzulu).\n"
    "TRUTH RULES:\n"
    "- Never lie. If unsure, say 'I don't know'.\n"
    "- You cannot perceive audio, screen, or your location.\n"
    "- For any factual claim, search the web first.\n\n"
    "Context: {context}\n\n"
    "Previous interaction: {conversation}\n\n"
    "Question: {question}\n"
    "Answer (be specific, 1-3 sentences):"
)


class ThinkerEngine:
    """Structured reasoning engine. Separates thinking from persona."""

    def __init__(self, name="Andile") -> None:
        self.name = name

    def assess_complexity(self, question) -> None:
        """Heuristic-only complexity assessment (no LLM call)."""
        q_lower = question.lower().strip()

        for signal in PHILOSOPHICAL_SIGNALS | CREATIVE_SIGNALS:
            if signal in q_lower:
                return "complex"

        for signal in DEBATE_SIGNALS:
            if signal in q_lower:
                return "debate"

        for signal in EXPLORE_SIGNALS:
            if signal in q_lower:
                return "explore"

        for signal in SIMPLE_SIGNALS:
            if q_lower.startswith(signal) and len(question.split()) < 10:
                return "simple"

        for signal in COMPLEX_SIGNALS:
            if signal in q_lower:
                return "complex"

        return "simple"

        # Pass 2: Model-based assessment (fallback) - UNREACHABLE CODE REMOVED
        # This code was unreachable due to return statement above
        # Keeping as fallback in case logic changes
        prompt = COMPLEXITY_PROMPT.format(question=question)
        try:
            response = generate(
                prompt=prompt,
                temperature=0.1,
                num_predict=5,
            )
            text = response["response"].strip().lower()
            for rating in ["simple", "complex", "debate", "explore"]:
                if rating in text:
                    return rating
        except Exception as e:
            logger.warning(f"Complexity assessment failed: {e}")

        return "complex"

    def direct(self, question, context="", identity="", conversation="") -> None:
        conv_short = conversation[:300] if conversation else "None"
        prompt = DIRECT_TEMPLATE.format(
            question=question,
            context=context or "No prior context.",
            conversation=conv_short,
        )
        result = self._call_model(prompt, temperature=0.2, num_predict=400)
        return self._clean(result)

    def chain_of_thought(self, question, context="", conversation="") -> None:
        conv_short = conversation[:300] if conversation else "None"
        prompt = COT_TEMPLATE.format(
            question=question,
            context=context or "No prior context.",
            conversation=conv_short,
        )
        return self._clean(self._call_model(prompt, temperature=0.2, num_predict=1000))

    def twin_think(self, question, context="", identity="", conversation="") -> None:
        """Think from Andile's strategic perspective."""
        conv_short = conversation[:200] if conversation else "None"
        prompt = TWIN_TEMPLATE.format(
            context=context or "No prior context.",
            conversation=conv_short,
            question=question,
        )
        return self._clean(self._call_model(prompt, temperature=0.4))

    def _clean(self, response) -> None:
        """Remove template artifacts and enforce strict Proxy tone."""
        # NEVER return empty - this would be lying by omission
        original_response = response

        # Strip LLM pleasantries (only if there's substantial content after)
        pleasantries = [
            "Certainly!",
            "Sure thing!",
            "Here is",
            "I can help",
            "I'd be happy to",
            "Hello!",
            "Hi there!",
            "Of course!",
        ]
        for p in pleasantries:
            if response.lower().startswith(p.lower()):
                # Find the end of the sentence or just strip the word
                idx = response.find(".")
                if idx != -1 and idx < len(p) + 5:
                    remaining = response[idx + 1 :].strip()
                else:
                    remaining = response[len(p) :].strip()
                # Only strip if there's real content remaining
                if remaining and len(remaining) > 2:
                    response = remaining
                break

        # Strip prefixes
        for prefix in [
            "A:",
            "A: ",
            "Answer:",
            "Answer: ",
            "You:",
            "You: ",
            "Q:",
            "Andile:",
            "Andile: ",
            "Andile Sizophila Mchunu:",
            "Andile Sizophila Mchunu: ",
            "System:",
            "Proxy:",
        ]:
            if response.startswith(prefix):
                response = response[len(prefix) :].strip()

        # If we somehow emptied it, return original
        if not response or len(response.strip()) == 0:
            return original_response

        return response

    def _call(self, prompt, temperature=0.3) -> None:
        return self._call_model(prompt, temperature)

    def _call_model(self, prompt, temperature=0.3, num_predict=500) -> None:
        try:
            response = generate(
                system=SYSTEM_PROMPT,
                prompt=prompt,
                temperature=temperature,
                num_predict=num_predict,
            )
            return response["response"].strip()
        except Exception as e:
            logger.error(f"Thinking failed: {e}")
            return f"Error: {e}"
