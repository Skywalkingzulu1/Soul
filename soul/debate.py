import logging

logger = logging.getLogger(__name__)

from soul.ollama_client import generate

ADVOCATE_PROMPT = (
    "You are an advocate. Your job is to argue FOR the best answer to this question.\n"
    "Be rigorous and logical. Build a strong case.\n\n"
    "Question: {question}\n"
    "Context: {context}\n"
    "Previous criticism: {criticism}\n\n"
    "Your argument:"
)

CRITIC_PROMPT = (
    "You are a critic. Your job is to find flaws and offer better alternatives.\n"
    "Be skeptical but fair. Don't just disagree — provide a better answer if possible.\n\n"
    "Question: {question}\n"
    "Advocate's argument: {argument}\n\n"
    "Your critique:"
)

JUDGE_PROMPT = (
    "You are a judge. Two thinkers have debated this question.\n"
    "Evaluate both arguments. Synthesize the best answer.\n"
    "Be decisive. State the final answer clearly.\n\n"
    "Question: {question}\n\n"
    "Advocate's final position:\n{advocate}\n\n"
    "Critic's final position:\n{critic}\n\n"
    "Your judgment (synthesize the best answer):"
)


class DebateSystem:
    """Multi-agent debate: advocate vs critic, judged by a third instance."""

    def __init__(self) -> None:
        pass  # Uses ollama_client.generate() with default model

    def run(self, question, context="", rounds=1) -> None:
        advocate_history = []
        critic_history = []

        for r in range(rounds):
            # Advocate speaks
            criticism = critic_history[-1] if critic_history else "None yet."
            a_prompt = ADVOCATE_PROMPT.format(
                question=question, context=context, criticism=criticism
            )
            a_response = self._call(a_prompt, temperature=0.5)
            advocate_history.append(a_response)
            logger.info(f"Debate round {r + 1}: Advocate spoke")

            # Critic responds
            b_prompt = CRITIC_PROMPT.format(
                question=question, argument=advocate_history[-1]
            )
            b_response = self._call(b_prompt, temperature=0.5)
            critic_history.append(b_response)
            logger.info(f"Debate round {r + 1}: Critic spoke")

        # Judge synthesizes
        judge_prompt = JUDGE_PROMPT.format(
            question=question,
            advocate=advocate_history[-1],
            critic=critic_history[-1],
        )
        judgment = self._call(judge_prompt, temperature=0.3)
        logger.info("Debate complete: Judge rendered verdict")
        return judgment

    def _call(self, prompt, temperature=0.3) -> None:
        try:
            response = generate(
                prompt=prompt,
                temperature=temperature,
                num_predict=1500,
            )
            return response["response"]
        except Exception as e:
            logger.error(f"Debate call failed: {e}")
            return f"Error during debate: {e}"
