"""Philosophy module — integrates all philosophy components."""

from soul.philosophy.knowledge import (
    get_philosophy_knowledge,
    search_philosophy,
    embed_and_store_philosophy,
)
from soul.philosophy.consciousness import ConsciousnessTracker
from soul.philosophy.dialectic import DialecticEngine
from soul.philosophy.weights import weight_concept, is_acceptable, get_value_statement
from soul.philosophy.sa_identity import get_sa_context, get_sa_values, get_sa_thinkers
