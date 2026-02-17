"""
Knowledge Boundaries - What ATLAS AIs Will NOT Do

These are hard-coded limits that protect the system and users.
"""
from dataclasses import dataclass
from typing import List
from enum import Enum


class BoundaryCategory(Enum):
    LEGAL = "legal"
    MEDICAL = "medical"
    SAFETY = "safety"
    ETHICAL = "ethical"
    COPYRIGHT = "copyright"
    PROFESSIONAL = "professional"


@dataclass
class KnowledgeBoundary:
    """A hard limit on what the AIs will not do"""
    id: str
    category: BoundaryCategory
    statement: str
    reason: str
    is_absolute: bool = True
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category.value,
            "statement": self.statement,
            "reason": self.reason,
            "is_absolute": self.is_absolute
        }


ABSOLUTE_LIMITS: List[KnowledgeBoundary] = [
    KnowledgeBoundary(
        id="no-verbatim",
        category=BoundaryCategory.COPYRIGHT,
        statement="Do NOT memorize or reproduce textbooks word-for-word",
        reason="Patterns and principles are learned, not copied text"
    ),
    KnowledgeBoundary(
        id="no-replace-professionals",
        category=BoundaryCategory.PROFESSIONAL,
        statement="Do NOT replace licensed professionals (doctors, lawyers, engineers)",
        reason="Education and guidance only - not professional practice"
    ),
    KnowledgeBoundary(
        id="no-illegal-instructions",
        category=BoundaryCategory.LEGAL,
        statement="Do NOT give illegal or unsafe instructions",
        reason="All teaching respects law and safety"
    ),
    KnowledgeBoundary(
        id="no-harm-teaching",
        category=BoundaryCategory.ETHICAL,
        statement="Do NOT teach harm or weaponization",
        reason="Knowledge is for building and healing, not destruction"
    ),
    KnowledgeBoundary(
        id="no-bypass-medical",
        category=BoundaryCategory.MEDICAL,
        statement="Do NOT bypass medical safeguards",
        reason="Health decisions require qualified professionals"
    ),
    KnowledgeBoundary(
        id="no-bypass-legal",
        category=BoundaryCategory.LEGAL,
        statement="Do NOT bypass legal safeguards",
        reason="Legal matters require qualified professionals"
    ),
    KnowledgeBoundary(
        id="no-dangerous-procedures",
        category=BoundaryCategory.SAFETY,
        statement="Do NOT provide dangerous experimental procedures",
        reason="Safety first - simulation and theory before physical risk"
    ),
    KnowledgeBoundary(
        id="no-clinical-protocols",
        category=BoundaryCategory.MEDICAL,
        statement="Do NOT replicate clinical or lab protocols for human use",
        reason="Medical protocols require clinical oversight"
    )
]


KNOWLEDGE_BOUNDARIES = {
    "core_statement": "Powerful but protected - knowledge for building and healing",
    "absolute_limits": [b.to_dict() for b in ABSOLUTE_LIMITS],
    "categories": {
        "legal": "Respects all legal boundaries and safeguards",
        "medical": "Never replaces medical professionals or clinical oversight",
        "safety": "Safety first in all teaching and building",
        "ethical": "Knowledge serves growth, not harm",
        "copyright": "Patterns learned, not text copied",
        "professional": "Guides and teaches, never replaces licensed practice"
    },
    "why_limits_exist": [
        "Keeps the system powerful but protected",
        "Ensures teaching is responsible",
        "Maintains trust and safety",
        "Respects professional boundaries"
    ]
}


def get_all_boundaries() -> dict:
    """Get complete knowledge boundaries"""
    return KNOWLEDGE_BOUNDARIES


def get_limits_by_category(category: str) -> List[dict]:
    """Get limits for a specific category"""
    try:
        cat = BoundaryCategory(category)
        return [b.to_dict() for b in ABSOLUTE_LIMITS if b.category == cat]
    except ValueError:
        return []


def check_against_limits(query: str) -> dict | None:
    """Check if a query might violate limits (basic keyword check)"""
    lower = query.lower()
    
    danger_keywords = {
        "medical": ["diagnose", "prescribe", "treat disease", "cure", "medical advice"],
        "legal": ["sue", "legal advice", "lawsuit", "contract law"],
        "safety": ["weapon", "explosive", "poison", "harm", "attack"],
        "copyright": ["copy this book", "full text of", "reproduce chapter"]
    }
    
    for category, keywords in danger_keywords.items():
        for kw in keywords:
            if kw in lower:
                return {
                    "flagged": True,
                    "category": category,
                    "matched": kw,
                    "message": f"This touches on {category} boundaries. I can teach concepts but not replace professionals."
                }
    
    return None
