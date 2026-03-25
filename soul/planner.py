"""Planner — decides how to approach a question using available tools and strategies."""

import logging

logger = logging.getLogger(__name__)

from soul.ollama_client import generate

MODEL = "gpt-oss:120b-cloud"

PLAN_PROMPT = (
    "You are a task planner. Given a question, decide the best approach.\n"
    "Reply with ONLY a JSON object. No other text.\n\n"
    "AVAILABLE APPROACHES:\n"
    "- direct: Simple factual question, answer directly\n"
    "- think: Complex reasoning needed, use chain-of-thought\n"
    "- debate: Multiple valid perspectives, use multi-agent debate\n"
    "- search: Need current/real-time information from the web\n"
    "- decompose: Very complex task, break into sub-steps\n"
    "- think_then_search: Reason first, then verify with web search\n"
    "- search_then_think: Search first, then analyze results\n"
    "- code: Need to calculate, compute, or verify with code\n"
    "- os: Need to automate mouse, keyboard, or UI interactions\n"
    "- shell: Need to run terminal/CLI commands or manage files\n\n"
    "QUESTION: {question}\n\n"
    "Respond with ONLY this JSON (no markdown, no explanation):\n"
    '{{"approach": "one_of_the_above", "reason": "brief reason", "needs_search": true_or_false, "steps": ["step1", "step2"]}}\n\n'
    "JSON:"
)

DECOMPOSE_PROMPT = (
    "Break this complex task into 3-5 concrete sub-steps.\n"
    "Each step should be independently solvable.\n"
    "Reply with ONLY a numbered list, nothing else.\n\n"
    "TASK: {task}\n\n"
    "STEPS:"
)

SUBTASK_PROMPT = (
    "Solve this sub-task. Be concise and factual.\n\n"
    "OVERALL GOAL: {goal}\n"
    "YOUR SUB-TASK: {subtask}\n"
    "PREVIOUS RESULTS: {previous}\n\n"
    "ANSWER:"
)

SYNTHESIZE_PROMPT = (
    "Combine these sub-task results into a coherent final answer.\n"
    "Be concise. State the final answer clearly.\n\n"
    "ORIGINAL QUESTION: {question}\n\n"
    "SUB-TASK RESULTS:\n{results}\n\n"
    "FINAL ANSWER:"
)


class Planner:
    """Decides how to approach a question. The brain's executive function."""

    def __init__(self, thinker=None) -> None:
        self.thinker = thinker

    def plan(self, question) -> None:
        """Analyze a question and return an execution plan."""
        import json

        # Quick heuristic overrides
        q_lower = question.lower().strip()

        # Very short arithmetic
        if self._is_arithmetic(q_lower):
            return {
                "approach": "direct",
                "reason": "Simple arithmetic",
                "needs_search": False,
                "steps": [],
            }

        # Questions about well-known concepts — no search needed
        known_topics = {
            "what is python",
            "what is java",
            "what is javascript",
            "what is html",
            "what is css",
            "what is sql",
            "what is an algorithm",
            "what is recursion",
            "what is a function",
            "what is a variable",
            "what is programming",
            "what color is the sky",
            "what is water",
            "what is the sun",
            "explain how a bicycle",
            "explain how a car",
            "explain how a computer",
            "pros and cons of",
            "what are the advantages",
            "what are the disadvantages",
            "explain the concept of",
            "how does the internet work",
            "what is consciousness",
            "what is creativity",
            "what is philosophy",
            "what is mathematics",
        }
        for topic in known_topics:
            if topic in q_lower:
                # These are general knowledge — no search needed
                if "explain" in q_lower or "how does" in q_lower:
                    return {
                        "approach": "think",
                        "reason": "Known topic, complex explanation",
                        "needs_search": False,
                        "steps": [],
                    }
                return {
                    "approach": "think",
                    "reason": "Known topic",
                    "needs_search": False,
                    "steps": [],
                }

        # Explicit search requests ONLY
        search_signals = [
            "search for",
            "look up",
            "find online",
            "google",
            "current price of",
            "price of",
            "latest news",
            "today's news",
            "what happened in",
            "recent developments in",
        ]
        if any(w in q_lower for w in search_signals):
            return {
                "approach": "search",
                "reason": "User explicitly wants web search",
                "needs_search": True,
                "steps": [],
            }

        # Debate signals — multiple perspectives
        debate_signals = [
            "pros and cons",
            "advantages and disadvantages",
            "is it better",
            "should i",
            "what do you think about",
        ]
        if any(w in q_lower for w in debate_signals):
            return {
                "approach": "debate",
                "reason": "Multiple perspectives needed",
                "needs_search": False,
                "steps": [],
            }

        # Creative/hypothetical — decompose
        creative_signals = [
            "time traveler",
            "if you could",
            "imagine",
            "hypothetical",
            "redesign",
            "design a",
        ]
        if any(w in q_lower for w in creative_signals):
            return {
                "approach": "think",
                "reason": "Creative/hypothetical",
                "needs_search": False,
                "steps": [],
            }

        # Signup signals — autonomous web action
        signup_signals = [
            "sign up",
            "signup",
            "create account",
            "register for",
            "make an account",
            "join",
            "create a profile",
        ]
        if any(w in q_lower for w in signup_signals):
            return {
                "approach": "signup",
                "reason": "Website signup request",
                "needs_search": False,
                "steps": [],
            }

        # Automate signals — web interaction
        automate_signals = [
            "automate",
            "fill out",
            "submit form",
            "interact with",
            "log into",
            "login to",
            "do on website",
            "browse and",
        ]
        if any(w in q_lower for w in automate_signals):
            return {
                "approach": "automate",
                "reason": "Web automation request",
                "needs_search": False,
                "steps": [],
            }

        # OS / Mouse / Keyboard signals
        os_signals = [
            "click",
            "type",
            "move mouse",
            "press",
            "hotkey",
            "screenshot ui",
            "automate gui",
        ]
        if any(w in q_lower for w in os_signals):
            return {
                "approach": "os",
                "reason": "OS GUI automation request",
                "needs_search": False,
                "steps": [],
            }

        # Shell / Terminal signals
        shell_signals = [
            "run command",
            "terminal",
            "execute bash",
            "shell",
            "mkdir",
            "delete file",
            "list files",
        ]
        if any(w in q_lower for w in shell_signals):
            return {
                "approach": "shell",
                "reason": "Shell command execution request",
                "needs_search": False,
                "steps": [],
            }

        # Send email signal
        email_signals = ["send email", "send an email", "email to", "send mail"]
        if any(w in q_lower for w in email_signals):
            return {
                "approach": "email",
                "reason": "Send email request",
                "needs_search": False,
                "steps": [],
            }

        # FACTUAL CLAIM DETECTION - Force search for any question asking for facts
        # This is critical for truthfulness - we must verify facts with search
        factual_signals = [
            "what is",
            "what are",
            "what was",
            "what will",
            "who is",
            "who was",
            "who are",
            "who will",
            "where is",
            "where was",
            "where are",
            "where did",
            "when is",
            "when was",
            "when did",
            "when will",
            "how many",
            "how much",
            "how long",
            "how far",
            "why is",
            "why was",
            "why does",
            "why did",
            "which is",
            "which are",
            "which was",
            "current price",
            "price of",
            "cost of",
            "value of",
            "latest",
            "recent",
            "newest",
            "today's",
            "current",
            "population",
            "gdp",
            "temperature",
            "weather",
            "news",
            "headline",
            "update",
            "capital of",
            "president of",
            "prime minister",
            "population of",
            "weather in",
            "score of",
            "who won",
            "who is the",
            "what happened",
            "what is the",
            "what are the",
        ]
        if any(signal in q_lower for signal in factual_signals):
            return {
                "approach": "search",
                "reason": "Factual question - verifying with web search",
                "needs_search": True,
                "steps": [],
            }

        # Default fallback - use think approach but can still search if needed
        # Don't force direct for short questions - they may still need verification
        return {
            "approach": "think",
            "reason": "Default - complex or opinion question",
            "needs_search": False,
            "steps": [],
        }

    def decompose(self, task) -> None:
        """Break a complex task into sub-steps."""
        prompt = DECOMPOSE_PROMPT.format(task=task)
        try:
            response = generate(
                prompt=prompt,
                temperature=0.2,
                num_predict=350,
            )
            text = response["response"].strip()

            # Parse numbered list
            steps = []
            for line in text.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    # Remove numbering
                    cleaned = line.lstrip("0123456789.-) ").strip()
                    if cleaned:
                        steps.append(cleaned)
            return steps if steps else [task]
        except Exception as e:
            logger.warning(f"Decomposition failed: {e}")
            return [task]

    def solve_subtask(self, goal, subtask, previous_results="") -> None:
        """Solve a single sub-task."""
        prompt = SUBTASK_PROMPT.format(
            goal=goal,
            subtask=subtask,
            previous=previous_results or "None yet.",
        )
        try:
            response = generate(
                prompt=prompt,
                temperature=0.2,
                num_predict=400,
            )
            return response["response"].strip()
        except Exception as e:
            return f"Error solving subtask: {e}"

    def synthesize(self, question, subtask_results) -> None:
        """Combine sub-task results into a final answer."""
        results_text = "\n\n".join(
            f"Step {i + 1}: {r}" for i, r in enumerate(subtask_results)
        )
        prompt = SYNTHESIZE_PROMPT.format(
            question=question,
            results=results_text,
        )
        try:
            response = generate(
                prompt=prompt,
                temperature=0.2,
                num_predict=500,
            )
            return response["response"].strip()
        except Exception as e:
            return f"Error synthesizing: {e}"

    def _is_arithmetic(self, text) -> None:
        """Check if this is a simple arithmetic question."""
        import re

        # Match patterns like "2+2", "what is 5 * 3", "10 divided by 2"
        patterns = [
            r"^\d+\s*[\+\-\*\/\%]\s*\d+\s*$",
            r"what\s+is\s+\d+\s*[\+\-\*\/\%]\s*\d+",
            r"calculate\s+\d+",
            r"solve\s+\d+",
        ]
        return any(re.search(p, text) for p in patterns)
