"""Agentic perception — understand what the screen shows using the LLM.

Takes a visual capture and asks the LLM to describe and analyze it.
"""

import logging

logger = logging.getLogger(__name__)

from soul.ollama_client import generate


def analyze_screen(screen_text, context=""):
    """Ask the LLM to analyze what's on screen.

    Args:
        screen_text: OCR text from the screen
        context: Additional context about what the user was doing

    Returns:
        str: Analysis of the screen content
    """
    if not screen_text or len(screen_text.strip()) < 5:
        return (
            "The screen appears to be empty, locked, or showing graphics without text."
        )

    prompt = (
        "Analyze what is shown on this computer screen. "
        "Describe what application is open, what the user sees, and what actions are possible.\n\n"
        f"SCREEN TEXT:\n{screen_text[:800]}\n\n"
        f"CONTEXT: {context or 'None'}\n\n"
        "Analysis:"
    )

    try:
        response = generate(
            system="You are analyzing a computer screen. Be concise and factual.",
            prompt=prompt,
            temperature=0.2,
            num_predict=500,
        )
        return response["response"].strip()
    except Exception as e:
        logger.error(f"Screen analysis failed: {e}")
        return f"Analysis error: {e}"


def decide_action(screen_text, analysis, goal=""):
    """Decide what action to take based on screen content.

    Args:
        screen_text: OCR text from screen
        analysis: Previous analysis of the screen
        goal: Current goal (if any)

    Returns:
        dict: {"action": str, "target": str, "reason": str}
    """
    prompt = (
        "Based on what's on screen, decide what action to take.\n\n"
        f"SCREEN: {screen_text[:500]}\n"
        f"ANALYSIS: {analysis[:300]}\n"
        f"GOAL: {goal or 'None specified'}\n\n"
        "Choose ONE action: click, type, scroll, wait, research, done\n"
        "If you need to interact with an element, describe what to click or type.\n\n"
        "Action:"
    )

    try:
        response = generate(
            system="You are deciding what computer action to take. Be concise.",
            prompt=prompt,
            temperature=0.2,
            num_predict=300,
        )
        text = response["response"].strip()

        # Parse action
        action = "wait"
        target = ""
        reason = text

        for a in ["click", "type", "scroll", "research", "done"]:
            if a in text.lower():
                action = a
                break

        return {"action": action, "target": target, "reason": reason}
    except Exception as e:
        logger.error(f"Action decision failed: {e}")
        return {"action": "wait", "target": "", "reason": f"Error: {e}"}
