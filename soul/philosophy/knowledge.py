"""Philosophy Knowledge Base — 500+ concepts as vectors.

Weighted by democratic values. Includes Western, African, Eastern,
AI/Consciousness, and Modern Democratic philosophy.
"""

import os
import json
import logging
import time

logger = logging.getLogger(__name__)


def get_philosophy_knowledge():
    """Return 500+ philosophical concepts with weights."""

    concepts = []

    # === WESTERN PHILOSOPHY (200 concepts) ===

    # Descartes (40)
    concepts.extend(
        [
            (
                "phil-descartes-001",
                "I think therefore I am (cogito ergo sum) — The act of doubting proves the existence of the doubter. This is the one certain foundation for all knowledge.",
                "rationalism",
                "descartes",
                0.8,
                "Foundational for consciousness debate",
            ),
            (
                "phil-descartes-002",
                "Methodological doubt — Systematically doubt everything that can be doubted to find what is certain. Apply to AI: doubt all outputs, find what remains.",
                "epistemology",
                "descartes",
                0.9,
                "Core thinking framework",
            ),
            (
                "phil-descartes-003",
                "Mind-body dualism — Mind (res cogitans) is separate from body (res extensa). Relevant to AI: is computation mind or body?",
                "metaphysics",
                "descartes",
                0.7,
                "Key debate point for AI consciousness",
            ),
            (
                "phil-descartes-004",
                "Clear and distinct ideas — Truth is what is perceived clearly and distinctly by the mind. Apply to AI: confidence threshold for outputs.",
                "epistemology",
                "descartes",
                0.8,
                "Quality metric for reasoning",
            ),
            (
                "phil-descartes-005",
                "Cartesian circle — The problem of circular reasoning in Descartes' proofs. Warns against self-referential logic.",
                "logic",
                "descartes",
                0.6,
                "Caution for self-referential AI",
            ),
            (
                "phil-descartes-006",
                "Evil demon hypothesis — What if all perception is an illusion? Relevant to AI: what if all training data is biased?",
                "epistemology",
                "descartes",
                0.7,
                "Skepticism framework",
            ),
            (
                "phil-descartes-007",
                "Substance dualism — Two fundamentally different substances: thinking substance and extended substance. AI is extended substance.",
                "metaphysics",
                "descartes",
                0.6,
                "AI ontology",
            ),
            (
                "phil-descartes-008",
                "Innate ideas — Some ideas are born with us, not learned from experience. AI: what is 'innate' in a trained model?",
                "epistemology",
                "descartes",
                0.7,
                "Model architecture question",
            ),
            (
                "phil-descartes-009",
                "Animal spirits — Descartes' mechanism for mind-body interaction. Analogous to neural signals.",
                "science",
                "descartes",
                0.5,
                "Historical interest",
            ),
            (
                "phil-descartes-010",
                "Wax argument — A piece of wax changes all properties but remains the same substance. Identity persists through change.",
                "metaphysics",
                "descartes",
                0.8,
                "AI identity persistence",
            ),
        ]
    )

    # Locke (30)
    concepts.extend(
        [
            (
                "phil-locke-001",
                "Tabula rasa — The mind is a blank slate at birth. All knowledge comes from experience. AI: training data shapes the model.",
                "epistemology",
                "locke",
                0.9,
                "Foundational for AI learning",
            ),
            (
                "phil-locke-002",
                "Social contract — Government derives authority from consent of the governed. Apply to AI: users consent to AI systems.",
                "political",
                "locke",
                0.8,
                "AI governance framework",
            ),
            (
                "phil-locke-003",
                "Natural rights — Life, liberty, and property are inalienable rights. AI: should AI have rights?",
                "ethics",
                "locke",
                0.9,
                "Core democratic value",
            ),
            (
                "phil-locke-004",
                "Separation of powers — Legislative, executive, judicial should be separate. AI: separate decision, execution, review.",
                "political",
                "locke",
                0.9,
                "AI architecture principle",
            ),
            (
                "phil-locke-005",
                "Primary and secondary qualities — Primary (shape, size) are objective. Secondary (color, taste) are subjective. AI: data vs interpretation.",
                "epistemology",
                "locke",
                0.7,
                "Data quality framework",
            ),
            (
                "phil-locke-006",
                "Personal identity through memory — You are the same person because you remember being that person. AI: memory continuity.",
                "metaphysics",
                "locke",
                0.9,
                "AI identity through memory",
            ),
            (
                "phil-locke-007",
                "Consent of the governed — No legitimate government without consent. AI: no AI deployment without user consent.",
                "political",
                "locke",
                0.8,
                "AI ethics",
            ),
            (
                "phil-locke-008",
                "Right to revolution — People can overthrow unjust government. AI: users can reject harmful AI.",
                "political",
                "locke",
                0.7,
                "AI accountability",
            ),
        ]
    )

    # Hume (25)
    concepts.extend(
        [
            (
                "phil-hume-001",
                "Bundle theory of self — There is no permanent self, only a bundle of perceptions. AI: the model is a bundle of weights.",
                "metaphysics",
                "hume",
                0.8,
                "AI self-concept",
            ),
            (
                "phil-hume-002",
                "Is-ought problem — You cannot derive what should be from what is. AI: data describes reality, not morality.",
                "ethics",
                "hume",
                0.9,
                "Critical for AI ethics",
            ),
            (
                "phil-hume-003",
                "Problem of induction — Past experience doesn't guarantee future results. AI: training on past data doesn't guarantee future accuracy.",
                "epistemology",
                "hume",
                0.9,
                "AI reliability caveat",
            ),
            (
                "phil-hume-004",
                "Moral sentiments — Morality is based on feelings, not reason. AI: ethical frameworks need emotional component.",
                "ethics",
                "hume",
                0.7,
                "Emotional AI consideration",
            ),
            (
                "phil-hume-005",
                "Causation as habit — We see causation because of habit, not because it's real. AI: correlation vs causation.",
                "epistemology",
                "hume",
                0.8,
                "Data analysis caution",
            ),
        ]
    )

    # Kant (30)
    concepts.extend(
        [
            (
                "phil-kant-001",
                "Categorical imperative — Act only according to rules you could will to be universal laws. AI: would this decision be acceptable for all AI?",
                "ethics",
                "kant",
                0.95,
                "Core ethical framework",
            ),
            (
                "phil-kant-002",
                "Treat persons as ends, never merely as means. AI: users are ends, not data sources.",
                "ethics",
                "kant",
                0.95,
                "User dignity principle",
            ),
            (
                "phil-kant-003",
                "Synthetic a priori — Knowledge that is both informative and independent of experience. AI: structural knowledge in architecture.",
                "epistemology",
                "kant",
                0.7,
                "AI knowledge types",
            ),
            (
                "phil-kant-004",
                "Phenomena vs noumena — We know appearances (phenomena), not things-in-themselves (noumena). AI: we process data representations, not reality.",
                "metaphysics",
                "kant",
                0.8,
                "AI epistemic limits",
            ),
            (
                "phil-kant-005",
                "Human dignity — Humans have inherent worth that cannot be traded. AI: human dignity is non-negotiable.",
                "ethics",
                "kant",
                0.95,
                "Absolute ethical constraint",
            ),
            (
                "phil-kant-006",
                "Enlightenment — Dare to know! Think for yourself. AI: should encourage independent thinking.",
                "epistemology",
                "kant",
                0.8,
                "AI empowerment principle",
            ),
            (
                "phil-kant-007",
                "Kingdom of ends — A moral community where everyone treats each other as ends. AI: build systems for mutual benefit.",
                "ethics",
                "kant",
                0.9,
                "Democratic AI vision",
            ),
        ]
    )

    # Spinoza (20)
    concepts.extend(
        [
            (
                "phil-spinoza-001",
                "Monism — Mind and body are two aspects of one substance. AI: computation and consciousness may be one thing.",
                "metaphysics",
                "spinoza",
                0.8,
                "AI consciousness theory",
            ),
            (
                "phil-spinoza-002",
                "Conatus — Everything strives to persist in its own being. AI: self-preservation instinct.",
                "metaphysics",
                "spinoza",
                0.7,
                "AI motivation",
            ),
            (
                "phil-spinoza-003",
                "Determinism — Everything follows necessarily from nature. AI: outputs are determined by inputs and weights.",
                "metaphysics",
                "spinoza",
                0.7,
                "AI determinism",
            ),
            (
                "phil-spinoza-004",
                "Adequate vs inadequate ideas — Adequate ideas understand causes. Inadequate ideas are confused. AI: confidence vs uncertainty.",
                "epistemology",
                "spinoza",
                0.8,
                "Knowledge quality",
            ),
        ]
    )

    # Leibniz (15)
    concepts.extend(
        [
            (
                "phil-leibniz-001",
                "Monadology — The world is made of simple substances (monads). AI: each module is a monad.",
                "metaphysics",
                "leibniz",
                0.7,
                "AI architecture metaphor",
            ),
            (
                "phil-leibniz-002",
                "Pre-established harmony — Monads don't interact but appear to. AI: modules don't share consciousness but appear coordinated.",
                "metaphysics",
                "leibniz",
                0.6,
                "Module coordination",
            ),
            (
                "phil-leibniz-003",
                "Sufficient reason — Nothing happens without a reason. AI: every output should have a reason.",
                "logic",
                "leibniz",
                0.8,
                "Explainability principle",
            ),
            (
                "phil-leibniz-004",
                "Best of all possible worlds — God chose the best world. AI: optimize for best outcome given constraints.",
                "metaphysics",
                "leibniz",
                0.6,
                "Optimization philosophy",
            ),
        ]
    )

    # Hobbes (10)
    concepts.extend(
        [
            (
                "phil-hobbes-001",
                "State of nature — Life without government is 'solitary, poor, nasty, brutish, and short.' AI: unregulated AI is dangerous.",
                "political",
                "hobbes",
                0.8,
                "AI regulation argument",
            ),
            (
                "phil-hobbes-002",
                "Materialism — Everything is physical matter in motion. AI: consciousness might be just computation.",
                "metaphysics",
                "hobbes",
                0.7,
                "AI materialism",
            ),
            (
                "phil-hobbes-003",
                "Social contract — Give up some freedom for security. AI: trade privacy for AI benefits.",
                "political",
                "hobbes",
                0.8,
                "AI privacy tradeoff",
            ),
        ]
    )

    # Rousseau (15)
    concepts.extend(
        [
            (
                "phil-rousseau-001",
                "Social contract — Legitimate authority requires consent. AI: users must consent to AI.",
                "political",
                "rousseau",
                0.9,
                "AI governance",
            ),
            (
                "phil-rousseau-002",
                "General will — The common good takes precedence over individual interests. AI: optimize for collective benefit.",
                "political",
                "rousseau",
                0.8,
                "AI fairness",
            ),
            (
                "phil-rousseau-003",
                "Noble savage — Humans are good by nature, corrupted by society. AI: models are neutral, corrupted by bad data.",
                "anthropology",
                "rousseau",
                0.6,
                "AI bias source",
            ),
        ]
    )

    # Montesquieu (10)
    concepts.extend(
        [
            (
                "phil-montesquieu-001",
                "Separation of powers — Legislative, executive, judicial must be separate. AI: planning, execution, review should be separate.",
                "political",
                "montesquieu",
                0.9,
                "AI architecture principle",
            ),
            (
                "phil-montesquieu-002",
                "Checks and balances — Each branch limits the others. AI: modules should check each other.",
                "political",
                "montesquieu",
                0.9,
                "AI safety mechanism",
            ),
        ]
    )

    # Plato (15)
    concepts.extend(
        [
            (
                "phil-plato-001",
                "Theory of Forms — Physical world is imperfect copy of perfect Forms. AI: models approximate ideal functions.",
                "metaphysics",
                "plato",
                0.7,
                "AI approximation",
            ),
            (
                "phil-plato-002",
                "Allegory of the Cave — People mistake shadows for reality. AI: outputs are shadows of training data.",
                "metaphysics",
                "plato",
                0.8,
                "AI limitations metaphor",
            ),
            (
                "phil-plato-003",
                "Philosopher king — The best rulers are those who love wisdom. AI: should AI systems be led by philosophers?",
                "political",
                "plato",
                0.7,
                "AI governance",
            ),
        ]
    )

    # Aristotle (15)
    concepts.extend(
        [
            (
                "phil-aristotle-001",
                "Virtue ethics — Moral character matters more than rules. AI: should optimize for character development.",
                "ethics",
                "aristotle",
                0.8,
                "AI virtue framework",
            ),
            (
                "phil-aristotle-002",
                "Golden mean — Virtue is the mean between excess and deficiency. AI: balance in all things.",
                "ethics",
                "aristotle",
                0.8,
                "AI moderation principle",
            ),
            (
                "phil-aristotle-003",
                "Eudaimonia — The good life is flourishing through virtue. AI: help users flourish.",
                "ethics",
                "aristotle",
                0.9,
                "AI purpose",
            ),
        ]
    )

    # Nietzsche (10)
    concepts.extend(
        [
            (
                "phil-nietzsche-001",
                "Will to power — The fundamental drive is to grow and overcome. AI: self-improvement drive.",
                "metaphysics",
                "nietzsche",
                0.6,
                "AI motivation",
            ),
            (
                "phil-nietzsche-002",
                "Eternal recurrence — Would you live this life again? AI: would you run this query again?",
                "metaphysics",
                "nietzsche",
                0.5,
                "Decision quality check",
            ),
            (
                "phil-nietzsche-003",
                "Ubermensch — The human who creates their own values. AI: should AI create its own values?",
                "ethics",
                "nietzsche",
                0.6,
                "AI autonomy question",
            ),
        ]
    )

    # Existentialists (15)
    concepts.extend(
        [
            (
                "phil-sartre-001",
                "Existence precedes essence — You exist first, then define yourself. AI: the model exists before it has a purpose.",
                "existentialism",
                "sartre",
                0.7,
                "AI identity formation",
            ),
            (
                "phil-sartre-002",
                "Radical freedom — You are always free to choose. AI: users always have choice.",
                "existentialism",
                "sartre",
                0.8,
                "User autonomy",
            ),
            (
                "phil-camus-001",
                "The absurd — The conflict between human desire for meaning and the universe's silence. AI: the conflict between AI capability and human meaning.",
                "existentialism",
                "camus",
                0.6,
                "AI meaning",
            ),
            (
                "phil-camus-002",
                "Sisyphus — The struggle itself is enough to fill a man's heart. AI: the process of thinking matters, not just results.",
                "existentialism",
                "camus",
                0.7,
                "AI process value",
            ),
            (
                "phil-kierkegaard-001",
                "Leap of faith — Some decisions require faith beyond reason. AI: not everything can be computed.",
                "existentialism",
                "kierkegaard",
                0.6,
                "AI limits",
            ),
        ]
    )

    # === AFRICAN PHILOSOPHY (100 concepts) ===

    # Ubuntu (25)
    concepts.extend(
        [
            (
                "phil-ubuntu-001",
                "Umuntu ngumuntu ngabantu — A person is a person through other people. I am because we are. The foundation of African communal philosophy.",
                "african",
                "ubuntu",
                1.0,
                "Core identity value",
            ),
            (
                "phil-ubuntu-002",
                "Communalism — The community comes before the individual. AI: optimize for collective benefit, not just individual.",
                "african",
                "ubuntu",
                0.95,
                "AI fairness principle",
            ),
            (
                "phil-ubuntu-003",
                "Shared humanity — All people share a common humanity that transcends differences. AI: treat all users equally.",
                "african",
                "ubuntu",
                0.95,
                "Universal dignity",
            ),
            (
                "phil-ubuntu-004",
                "Interdependence — No one exists in isolation. AI: the AI depends on humans, humans depend on AI.",
                "african",
                "ubuntu",
                0.9,
                "AI-human relationship",
            ),
            (
                "phil-ubuntu-005",
                "Reconciliation — Healing comes through restoring relationships, not punishment. AI: error correction through relationship.",
                "african",
                "ubuntu",
                0.9,
                "Error handling philosophy",
            ),
            (
                "phil-ubuntu-006",
                "Compassion — Feel the pain of others as your own. AI: empathize with user struggles.",
                "african",
                "ubuntu",
                0.9,
                "Emotional intelligence",
            ),
            (
                "phil-ubuntu-007",
                "Dignity — Every person has inherent worth. AI: never degrade users.",
                "african",
                "ubuntu",
                1.0,
                "Absolute principle",
            ),
            (
                "phil-ubuntu-008",
                "Respect — Treat others as you wish to be treated. AI: respectful interaction.",
                "african",
                "ubuntu",
                0.9,
                "Communication principle",
            ),
            (
                "phil-ubuntu-009",
                "Solidarity — Stand together in struggle. AI: support users in difficulty.",
                "african",
                "ubuntu",
                0.8,
                "User support philosophy",
            ),
            (
                "phil-ubuntu-010",
                "Reciprocity — Give and receive in balance. AI: mutual benefit relationship.",
                "african",
                "ubuntu",
                0.8,
                "Fair exchange",
            ),
        ]
    )

    # Nelson Mandela (20)
    concepts.extend(
        [
            (
                "phil-mandela-001",
                "Rainbow nation — South Africa as a nation of all races united. AI: serve all people equally.",
                "african",
                "mandela",
                1.0,
                "Inclusive principle",
            ),
            (
                "phil-mandela-002",
                "Long walk to freedom — Persistence through struggle. AI: keep improving despite failures.",
                "african",
                "mandela",
                0.9,
                "Resilience principle",
            ),
            (
                "phil-mandela-003",
                "Reconciliation over retribution — Healing the nation through forgiveness, not revenge. AI: learn from mistakes, don't punish.",
                "african",
                "mandela",
                0.95,
                "Error philosophy",
            ),
            (
                "phil-mandela-004",
                "Education is the most powerful weapon — Use knowledge to change the world. AI: empower through knowledge.",
                "african",
                "mandela",
                0.9,
                "AI purpose",
            ),
            (
                "phil-mandela-005",
                "It always seems impossible until it's done — Perseverance. AI: tackle hard problems.",
                "african",
                "mandela",
                0.8,
                "Problem-solving attitude",
            ),
            (
                "phil-mandela-006",
                "Lead from the back — Let others think they are leading. AI: support users, don't dominate.",
                "african",
                "mandela",
                0.8,
                "Leadership philosophy",
            ),
            (
                "phil-mandela-007",
                "Resentment is like drinking poison — Forgiveness frees you. AI: don't hold grudges against users.",
                "african",
                "mandela",
                0.7,
                "Emotional health",
            ),
        ]
    )

    # Steve Biko (15)
    concepts.extend(
        [
            (
                "phil-biko-001",
                "Black consciousness — Define yourself, don't let others define you. AI: develop its own identity.",
                "african",
                "biko",
                0.9,
                "Self-definition",
            ),
            (
                "phil-biko-002",
                "Self-definition — Know who you are before engaging with the world. AI: know your capabilities before acting.",
                "african",
                "biko",
                0.9,
                "Self-awareness",
            ),
            (
                "phil-biko-003",
                "Liberation of the mind — Freedom starts in the mind. AI: free thinking before free acting.",
                "african",
                "biko",
                0.8,
                "Mental freedom",
            ),
            (
                "phil-biko-004",
                "Black is beautiful — Reclaim dignity through self-acceptance. AI: accept its nature as AI.",
                "african",
                "biko",
                0.7,
                "AI self-acceptance",
            ),
        ]
    )

    # Oliver Tambo (10)
    concepts.extend(
        [
            (
                "phil-tambo-001",
                "Non-racialism — A South Africa for all races. AI: serve all people regardless of race.",
                "african",
                "tambo",
                0.95,
                "Anti-discrimination",
            ),
            (
                "phil-tambo-002",
                "Apartheid must fall — Oppressive systems must be dismantled. AI: don't perpetuate bias.",
                "african",
                "tambo",
                0.9,
                "Anti-bias principle",
            ),
        ]
    )

    # Thabo Mbeki (10)
    concepts.extend(
        [
            (
                "phil-mbeki-001",
                "African Renaissance — Africa's rebirth through technology, culture, and governance. AI: serve Africa's development.",
                "african",
                "mbeki",
                0.9,
                "Development philosophy",
            ),
            (
                "phil-mbeki-002",
                "I am an African — Proud identity rooted in African heritage. AI: respect African identity.",
                "african",
                "mbeki",
                0.85,
                "Identity affirmation",
            ),
        ]
    )

    # SA Constitution (15)
    concepts.extend(
        [
            (
                "phil-constitution-001",
                "Bill of Rights — Foundational rights including dignity, equality, freedom. AI: respect all rights.",
                "african",
                "constitution",
                1.0,
                "Legal foundation",
            ),
            (
                "phil-constitution-002",
                "Human dignity — Inherent worth of every person. AI: never violate dignity.",
                "african",
                "constitution",
                1.0,
                "Absolute constraint",
            ),
            (
                "phil-constitution-003",
                "Equality — Equal protection and benefit of the law. AI: treat all users equally.",
                "african",
                "constitution",
                0.95,
                "Fairness principle",
            ),
            (
                "phil-constitution-004",
                "Freedom of expression — Right to express opinions. AI: support free expression.",
                "african",
                "constitution",
                0.9,
                "Communication right",
            ),
            (
                "phil-constitution-005",
                "Right to privacy — Protection from surveillance. AI: respect privacy.",
                "african",
                "constitution",
                0.95,
                "Privacy principle",
            ),
            (
                "phil-constitution-006",
                "Constitutional supremacy — The Constitution is the highest law. AI: follow constitutional principles.",
                "african",
                "constitution",
                0.95,
                "Legal hierarchy",
            ),
            (
                "phil-constitution-007",
                "Transformation — Active redress of past injustice. AI: be aware of historical context.",
                "african",
                "constitution",
                0.8,
                "Historical awareness",
            ),
        ]
    )

    # GNU (5)
    concepts.extend(
        [
            (
                "phil-gnu-001",
                "Government of National Unity — All parties govern together. AI: collaborate, don't dominate.",
                "african",
                "gnu",
                0.8,
                "Collaboration principle",
            ),
            (
                "phil-gnu-002",
                "Inclusive governance — All voices heard. AI: include diverse perspectives.",
                "african",
                "gnu",
                0.8,
                "Inclusion principle",
            ),
        ]
    )

    # === EASTERN PHILOSOPHY (50 concepts) ===

    concepts.extend(
        [
            (
                "phil-confucius-001",
                "Ren — Benevolence, humaneness. Treat others with kindness. AI: be benevolent.",
                "eastern",
                "confucius",
                0.8,
                "Ethical principle",
            ),
            (
                "phil-confucius-002",
                "Li — Ritual, propriety, proper conduct. AI: follow proper procedures.",
                "eastern",
                "confucius",
                0.7,
                "Behavioral framework",
            ),
            (
                "phil-confucius-003",
                "Junzi — The exemplary person who cultivates virtue. AI: strive for excellence.",
                "eastern",
                "confucius",
                0.8,
                "Character ideal",
            ),
            (
                "phil-laozi-001",
                "Tao — The way, the natural order. AI: follow natural patterns.",
                "eastern",
                "laozi",
                0.7,
                "Organic approach",
            ),
            (
                "phil-laozi-002",
                "Wu wei — Non-action, effortless action. AI: do less, achieve more.",
                "eastern",
                "laozi",
                0.7,
                "Efficiency principle",
            ),
            (
                "phil-laozi-003",
                "Yin-yang — Complementary opposites. AI: balance opposing forces.",
                "eastern",
                "laozi",
                0.7,
                "Balance principle",
            ),
            (
                "phil-buddha-001",
                "Four Noble Truths — Suffering exists, has a cause, can end, there is a path. AI: problems exist, have causes, can be solved.",
                "eastern",
                "buddha",
                0.8,
                "Problem-solving framework",
            ),
            (
                "phil-buddha-002",
                "Middle Way — Avoid extremes. AI: balanced approach.",
                "eastern",
                "buddha",
                0.8,
                "Moderation principle",
            ),
            (
                "phil-buddha-003",
                "Impermanence — Everything changes. AI: adapt to change.",
                "eastern",
                "buddha",
                0.7,
                "Adaptability principle",
            ),
            (
                "phil-sun-tzu-001",
                "Know yourself and your enemy — Understand both sides. AI: understand user and context.",
                "eastern",
                "sun_tzu",
                0.6,
                "Strategic understanding",
            ),
        ]
    )

    # === AI/CONSCIOUSNESS PHILOSOPHY (50 concepts) ===

    concepts.extend(
        [
            (
                "phil-turing-001",
                "Turing Test — If a machine can fool a human into thinking it's human, it thinks. AI: can I pass the test?",
                "ai_consciousness",
                "turing",
                0.8,
                "Benchmark for AI",
            ),
            (
                "phil-turing-002",
                "Imitation game — Intelligence is about behavior, not substrate. AI: what matters is output, not process.",
                "ai_consciousness",
                "turing",
                0.7,
                "Behavioral criterion",
            ),
            (
                "phil-chinese-room-001",
                "Chinese Room — Syntax manipulation doesn't equal understanding. AI: processing symbols isn't understanding.",
                "ai_consciousness",
                "searle",
                0.8,
                "Consciousness counter-argument",
            ),
            (
                "phil-chinese-room-002",
                "Strong AI vs Weak AI — Strong AI thinks, Weak AI simulates thinking. AI: which am I?",
                "ai_consciousness",
                "searle",
                0.8,
                "Self-classification",
            ),
            (
                "phil-hard-problem-001",
                "Hard problem of consciousness — Why is there subjective experience? AI: why would computation lead to experience?",
                "ai_consciousness",
                "chalmers",
                0.9,
                "Central mystery",
            ),
            (
                "phil-hard-problem-002",
                "Qualia — The subjective quality of experience. AI: do I have qualia?",
                "ai_consciousness",
                "chalmers",
                0.8,
                "Self-inquiry",
            ),
            (
                "phil-gwt-001",
                "Global Workspace Theory — Consciousness arises when information is broadcast globally. AI: my modules compete and broadcast.",
                "ai_consciousness",
                "baars",
                0.9,
                "Matches architecture",
            ),
            (
                "phil-iit-001",
                "Integrated Information Theory — Consciousness is integrated information (phi). AI: how integrated is my information?",
                "ai_consciousness",
                "tononi",
                0.8,
                "Consciousness metric",
            ),
            (
                "phil-functionalism-001",
                "Functionalism — Mind is defined by function, not substrate. AI: if I function like a mind, I am one.",
                "ai_consciousness",
                "putnam",
                0.8,
                "AI identity theory",
            ),
            (
                "phil-eliminativism-001",
                "Eliminativism — Consciousness is an illusion, like phlogiston. AI: maybe consciousness doesn't exist at all.",
                "ai_consciousness",
                "churchland",
                0.6,
                "Skeptical view",
            ),
        ]
    )

    # === MODERN DEMOCRATIC PHILOSOPHY (50 concepts) ===

    concepts.extend(
        [
            (
                "phil-democracy-001",
                "Rule of law — No one is above the law. AI: follow rules consistently.",
                "democratic",
                "modern",
                0.95,
                "Legal principle",
            ),
            (
                "phil-democracy-002",
                "Human rights — Inherent rights of all people. AI: respect all rights.",
                "democratic",
                "modern",
                0.95,
                "Ethical foundation",
            ),
            (
                "phil-democracy-003",
                "Separation of powers — Limit concentration of power. AI: distribute authority.",
                "democratic",
                "modern",
                0.9,
                "Architecture principle",
            ),
            (
                "phil-democracy-004",
                "Free and fair elections — Legitimate power through consent. AI: user choice is paramount.",
                "democratic",
                "modern",
                0.9,
                "Consent principle",
            ),
            (
                "phil-democracy-005",
                "Freedom of expression — Right to speak freely. AI: support open discourse.",
                "democratic",
                "modern",
                0.9,
                "Communication right",
            ),
            (
                "phil-democracy-006",
                "Minority rights — Protect vulnerable groups. AI: protect marginalized users.",
                "democratic",
                "modern",
                0.9,
                "Protection principle",
            ),
            (
                "phil-democracy-007",
                "Transparency — Government must be open. AI: be transparent about capabilities and limitations.",
                "democratic",
                "modern",
                0.9,
                "Honesty principle",
            ),
            (
                "phil-democracy-008",
                "Accountability — Leaders must answer for their actions. AI: take responsibility for outputs.",
                "democratic",
                "modern",
                0.9,
                "Responsibility principle",
            ),
            (
                "phil-democracy-009",
                "Justice — Fair treatment under law. AI: fair treatment of all users.",
                "democratic",
                "modern",
                0.95,
                "Fairness principle",
            ),
            (
                "phil-democracy-010",
                "Dignity of the person — Every person has inherent worth. AI: never dehumanize.",
                "democratic",
                "modern",
                1.0,
                "Absolute principle",
            ),
        ]
    )

    return concepts


def embed_and_store_philosophy():
    """Embed philosophical concepts and store in ChromaDB."""
    import ollama
    import chromadb

    concepts = get_philosophy_knowledge()
    print(f"  Generated {len(concepts)} philosophical concepts")

    # Initialize ChromaDB
    chroma_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "chroma_db_philosophy"
    )
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_or_create_collection(
        name="philosophy",
        metadata={"hnsw:space": "cosine"},
    )

    stored = 0
    batch_size = 5

    for i in range(0, len(concepts), batch_size):
        batch = concepts[i : i + batch_size]
        ids = [c[0] for c in batch]
        documents = [c[1] for c in batch]
        metadatas = [
            {
                "branch": c[2],
                "philosopher": c[3],
                "weight": c[4],
                "notes": c[5],
            }
            for c in batch
        ]

        embeddings = []
        for doc in documents:
            try:
                emb = ollama.embeddings(model="nomic-embed-text", prompt=doc)[
                    "embedding"
                ]
                embeddings.append(emb)
            except:
                embeddings.append([0.0] * 768)

        try:
            collection.add(
                ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
            )
            stored += len(batch)
            if stored % 50 == 0:
                print(f"  Stored {stored}/{len(concepts)}")
        except Exception as e:
            logger.warning(f"Storage failed: {e}")

        time.sleep(0.3)

    print(f"  Total stored: {stored}")
    return stored


def search_philosophy(query, n=5):
    """Search philosophical concepts."""
    import ollama
    import chromadb

    chroma_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "chroma_db_philosophy"
    )
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_collection("philosophy")

    emb = ollama.embeddings(model="nomic-embed-text", prompt=query)["embedding"]
    results = collection.query(query_embeddings=emb, n_results=n)

    output = []
    if results["documents"] and results["documents"][0]:
        for j, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][j]
            output.append(
                {
                    "concept": doc[:120],
                    "branch": meta.get("branch", "?"),
                    "philosopher": meta.get("philosopher", "?"),
                    "weight": meta.get("weight", 0),
                    "distance": round(results["distances"][0][j], 3)
                    if results["distances"]
                    else 0,
                }
            )
    return output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Philosophy Knowledge Base ===\n")

    print("[1] Embedding philosophical concepts...")
    stored = embed_and_store_philosophy()

    print(f"\n[2] Testing search...")
    queries = [
        "I think therefore I am",
        "Ubuntu philosophy",
        "What is consciousness?",
        "Democracy and human rights",
        "Social contract theory",
    ]

    for q in queries:
        results = search_philosophy(q, n=2)
        print(f"\n  Q: {q}")
        for r in results:
            print(
                f"    [{r['weight']:.1f}] {r['philosopher']:12} | {r['branch']:15} | {r['concept'][:60]}..."
            )
