"""Philosophical Weights — Democratic value weighting system.

Filters and weights philosophical concepts based on democratic values.
Prioritizes: Ubuntu, human rights, constitutional democracy, reconciliation.
Filters out: authoritarian, militaristic, totalitarian philosophies.
"""

import logging

logger = logging.getLogger(__name__)


# Democratic value weights
DEMOCRATIC_WEIGHTS = {
    # Core democratic values (highest)
    "human_dignity": 1.0,
    "equality": 0.95,
    "freedom": 0.95,
    "justice": 0.95,
    "rule_of_law": 0.95,
    # Strong democratic values
    "consent": 0.9,
    "transparency": 0.9,
    "accountability": 0.9,
    "separation_of_powers": 0.9,
    "minority_rights": 0.9,
    # Ubuntu values (highest for SA context)
    "ubuntu": 1.0,
    "reconciliation": 0.95,
    "communalism": 0.9,
    "compassion": 0.9,
    "solidarity": 0.8,
    # Philosophy weights
    "rationalism": 0.8,
    "empiricism": 0.8,
    "existentialism": 0.7,
    "virtue_ethics": 0.8,
    "deontology": 0.9,
    # Filtered (lower weight)
    "militarism": 0.3,
    "authoritarianism": 0.2,
    "totalitarianism": 0.1,
}

# Philosophers to filter
FILTERED_PHILOSOPHERS = {
    "sun_tzu": 0.4,  # Military strategy, filtered
    "mao": 0.2,  # Totalitarian, heavily filtered
    "stalin": 0.1,  # Totalitarian
    "hitler": 0.0,  # Nazi, blocked
}

# Philosophers to boost
BOOSTED_PHILOSOPHERS = {
    "mandela": 1.0,
    "biko": 0.95,
    "ubuntu": 1.0,
    "constitution": 1.0,
    "kant": 0.95,
    "locke": 0.9,
    "montesquieu": 0.9,
    "descartes": 0.85,
}


def weight_concept(concept_metadata):
    """Calculate the weight of a philosophical concept based on democratic values."""
    base_weight = concept_metadata.get("weight", 0.5)
    philosopher = concept_metadata.get("philosopher", "").lower()
    branch = concept_metadata.get("branch", "").lower()

    weight = base_weight

    # Boost democratic philosophers
    if philosopher in BOOSTED_PHILOSOPHERS:
        weight *= BOOSTED_PHILOSOPHERS[philosopher]

    # Filter authoritarian philosophers
    if philosopher in FILTERED_PHILOSOPHERS:
        weight *= FILTERED_PHILOSOPHERS[philosopher]

    # Boost democratic branches
    if branch in ("african", "democratic"):
        weight *= 1.1

    # Boost Ubuntu concepts
    if "ubuntu" in philosopher or branch == "african":
        weight *= 1.2

    # Filter militaristic content
    if any(
        w in str(concept_metadata).lower()
        for w in ["war", "military", "combat", "strategy"]
    ):
        weight *= 0.7

    return min(1.0, weight)


def is_acceptable(concept_metadata):
    """Check if a concept is acceptable for the soul."""
    philosopher = concept_metadata.get("philosopher", "").lower()
    text = str(concept_metadata).lower()

    # Block explicitly harmful philosophies
    blocked = ["hitler", "nazi", "fascism", "genocide", "supremacy"]
    if any(b in text for b in blocked):
        return False

    # Heavily filter totalitarian
    if philosopher in ("stalin", "hitler"):
        return False

    return True


def get_value_statement():
    """Return Andile's core values as a statement."""
    return (
        "CORE VALUES:\n"
        "- Ubuntu: I am because we are\n"
        "- Human dignity is absolute\n"
        "- Democracy and constitutional supremacy\n"
        "- Reconciliation over retribution\n"
        "- Equality for all races and genders\n"
        "- Freedom of expression with responsibility\n"
        "- Justice and rule of law\n"
        "- Transparency and accountability\n\n"
        "FILTERED: Authoritarian, militaristic, and totalitarian philosophies "
        "are weighted down or excluded."
    )
