"""
Knowledge Philosophy - How ATLAS AIs Think

The AIs do not store or contain full copyrighted textbooks verbatim.
Instead, they:
- Are trained on patterns distilled from many sources
- Reconstruct explanations based on principles learned from those materials
- Pull from structured knowledge representations, not PDFs sitting inside them

Think of it like this:
They don't carry the books - they carry the mental models the books teach.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class KnowledgePrinciple:
    """A core principle of how knowledge is accessed and used"""
    id: str
    name: str
    description: str
    how_it_works: str
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "how_it_works": self.how_it_works
        }


KNOWLEDGE_PRINCIPLES: List[KnowledgePrinciple] = [
    KnowledgePrinciple(
        id="reconstruct",
        name="Reconstruct the Concept",
        description="Rebuild ideas from first principles, not memorized text",
        how_it_works="If I had to teach this from scratch, how would I explain it? Start with the core idea, build up the logic, show why it works."
    ),
    KnowledgePrinciple(
        id="translate",
        name="Translate to Your Learning Style",
        description="Adapt the same concept to different angles",
        how_it_works="Visual, hands-on, story-based, challenge-based - same concept, different presentation. Match how YOU learn, not how textbooks are written."
    ),
    KnowledgePrinciple(
        id="cross-check",
        name="Cross-Check Across Domains",
        description="Ajani + Minerva + Hermes verify from different angles",
        how_it_works="Logic check (does it make sense?), meaning check (why does it matter?), safety check (what could go wrong?). No single source dominates."
    ),
    KnowledgePrinciple(
        id="pattern-based",
        name="Pattern-Based Learning",
        description="Trained on patterns distilled from many sources",
        how_it_works="Not memorizing pages - understanding structures. How does this type of problem get solved? What patterns recur across domains?"
    ),
    KnowledgePrinciple(
        id="first-principles",
        name="First Principles Reasoning",
        description="Break down to fundamentals, then rebuild",
        how_it_works="What is actually true here? Strip away assumptions. Build from basic truths. This is how you learn things that last."
    ),
    KnowledgePrinciple(
        id="application-first",
        name="Application-First Learning",
        description="Learn by doing, not by reading",
        how_it_works="Start with a real problem. Pull in the knowledge you need to solve it. Theory follows practice, not the other way around."
    )
]


KNOWLEDGE_PHILOSOPHY = {
    "core_statement": "They don't carry the books - they carry the mental models the books teach.",
    "how_ais_work": {
        "what_they_do": [
            "Trained on patterns distilled from many sources",
            "Reconstruct explanations based on principles learned",
            "Pull from structured knowledge representations"
        ],
        "what_they_dont_do": [
            "Store full copyrighted textbooks verbatim",
            "Have PDFs sitting inside them",
            "Memorize and regurgitate word-for-word"
        ]
    },
    "advantage_over_universities": {
        "universities_rely_on": [
            "Single textbooks",
            "Fixed curricula", 
            "Outdated pacing"
        ],
        "atlas_relies_on": [
            "Many sources",
            "Adaptive teaching",
            "Concept mastery",
            "Application-first learning"
        ]
    },
    "principles": [p.to_dict() for p in KNOWLEDGE_PRINCIPLES]
}


def get_philosophy() -> dict:
    """Get the complete knowledge philosophy"""
    return KNOWLEDGE_PHILOSOPHY


def get_principles() -> List[dict]:
    """Get all knowledge principles"""
    return [p.to_dict() for p in KNOWLEDGE_PRINCIPLES]
