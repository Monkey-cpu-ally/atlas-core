"""Topic router — domain-based lead AI selection.

Used across Atlas (Council tile, Teaching engine, Sandbox auto-mentor) to
pick which of Ajani / Minerva / Hermes should lead a given subject. When
no keyword matches, the request falls through to the Council (all three
weigh in).
"""
from __future__ import annotations
from typing import Tuple

# Per-AI keyword lexicon. Order is irrelevant — we match anywhere in the
# normalised topic string. Keep these lowercase, no leading/trailing
# whitespace.
AJANI_KEYWORDS = [
    "engineering", "physics", "math", "mathematics", "architecture",
    "robotics", "energy", "aerospace", "mechanics", "kinetic", "resonance",
    "power", "solar", "battery", "bridge", "structure", "construction",
    "load", "stress", "thermodynamic", "rocket", "propulsion", "build",
]

MINERVA_KEYWORDS = [
    "biology", "botany", "medicine", "history", "mythology", "psychology",
    "culture", "ecology", "ecosystem", "biodivers", "ethics",
    "society", "human", "narrative", "story", "spirit", "community",
    "wisdom", "tradition", "anthropology", "permaculture", "wildlife",
    "climate", "language", "literature", "art",
]
# Note on routing priority: AJANI → MINERVA → HERMES → COUNCIL. Multi-domain
# topics short-circuit at the first match. "philosophy" intentionally falls
# through to council because the keyword set excludes it — the original spec
# expects /api/council/route {'topic':'philosophy of mind'} → council.

HERMES_KEYWORDS = [
    "coding", "code", "computer science", "ai", "cybersecurity",
    "electronics", "software", "algorithm", "data", "machine learning",
    "neural", "nano", "swarm", "complexity", "pattern", "automation",
    "network", "protocol", "encryption", "blockchain", "logic", "program",
    "debugging", "compiler", "operating system",
]


def route_topic(topic: str) -> Tuple[str, str]:
    """Pick the lead AI for a topic.

    Returns (ai_id, matched_keyword). When no keyword matches, returns
    ('council', '') so the caller can fan out to all three.
    """
    if not topic:
        return ("council", "")
    t = topic.lower()

    for kw in AJANI_KEYWORDS:
        if kw in t:
            return ("ajani", kw)
    for kw in MINERVA_KEYWORDS:
        if kw in t:
            return ("minerva", kw)
    for kw in HERMES_KEYWORDS:
        if kw in t:
            return ("hermes", kw)

    return ("council", "")


# Display metadata kept alongside the router so callers can render the
# routing result without reaching into atlasCore.js mappings.
AI_DISPLAY = {
    "ajani":   {"name": "AJANI",   "color": "#F03246", "role": "Builder · Strategist · Engineer",
                "domain": "Elemental kinetics, structural physics, energy systems."},
    "minerva": {"name": "MINERVA", "color": "#28C8BE", "role": "Wisdom Keeper · Reflector · Ethicist",
                "domain": "Living systems, human impact, culture, narrative."},
    "hermes":  {"name": "HERMES",  "color": "#E0E0EA", "role": "Pattern Hunter · Code · Systems",
                "domain": "Algorithms, networks, nanoscale, edge-case logic."},
    "council": {"name": "COUNCIL", "color": "#A878E6", "role": "Tri-AI Deliberation",
                "domain": "Cross-domain or ambiguous topics route here."},
}
