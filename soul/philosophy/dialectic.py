"""Dialectic Engine — Socratic method, thesis-antithesis-synthesis.

Enables Andile to engage in philosophical debate using
structured argumentation.
"""

import logging

logger = logging.getLogger(__name__)


class DialecticEngine:
    """Simulated philosophical debate using thesis-antithesis-synthesis."""

    def __init__(self, knowledge_search_func=None):
        self.search = knowledge_search_func
        self.debates = []

    def socratic_question(self, proposition):
        """Generate Socratic questions to examine a proposition."""
        questions = [
            f"What do you mean by '{proposition}'?",
            f"How do you know '{proposition}' is true?",
            f"What evidence supports '{proposition}'?",
            f"What would contradict '{proposition}'?",
            f"Are there exceptions to '{proposition}'?",
            f"What are the consequences if '{proposition}' is false?",
            f"Who disagrees with '{proposition}' and why?",
            f"Is '{proposition}' universally true or context-dependent?",
        ]
        return questions

    def thesis_antithesis(self, proposition):
        """Generate thesis and antithesis for a proposition."""
        # Search philosophy knowledge for supporting/opposing views
        supporting = []
        opposing = []

        if self.search:
            try:
                results = self.search(proposition, n=3)
                for r in results:
                    if r.get("weight", 0) > 0.7:
                        supporting.append(r)
                    else:
                        opposing.append(r)
            except:
                pass

        thesis = {
            "position": f"FOR: {proposition}",
            "supporting_concepts": [s.get("concept", "")[:100] for s in supporting[:3]],
            "argument": f"The proposition '{proposition}' is supported by philosophical tradition.",
        }

        antithesis = {
            "position": f"AGAINST: {proposition}",
            "opposing_concepts": [o.get("concept", "")[:100] for o in opposing[:3]],
            "argument": f"The proposition '{proposition}' can be challenged on several grounds.",
            "counter_questions": self.socratic_question(proposition)[:3],
        }

        return thesis, antithesis

    def synthesize(self, thesis, antithesis):
        """Combine thesis and antithesis into higher understanding."""
        synthesis = {
            "thesis": thesis["position"],
            "antithesis": antithesis["position"],
            "synthesis": (
                f"Both perspectives have merit. "
                f"{thesis['position']} captures an important truth, while "
                f"{antithesis['position']} reveals important limitations. "
                f"A more nuanced position would acknowledge both."
            ),
            "new_questions": [
                "What conditions make the thesis true?",
                "What conditions make the antithesis true?",
                "Is there a higher framework that includes both?",
            ],
        }

        self.debates.append(synthesis)
        return synthesis

    def full_dialectic(self, proposition):
        """Run full thesis-antithesis-synthesis cycle."""
        thesis, antithesis = self.thesis_antithesis(proposition)
        synthesis = self.synthesize(thesis, antithesis)

        return {
            "proposition": proposition,
            "thesis": thesis,
            "antithesis": antithesis,
            "synthesis": synthesis,
            "socratic_questions": self.socratic_question(proposition),
        }

    def get_debate_history(self):
        return self.debates[-10:]
