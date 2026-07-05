from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DesignConcept:
    name: str
    category: str
    description: str
    materials: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    intended_emotion: str = ""


@dataclass
class DesignCritique:
    first_impression: str
    strengths: List[str]
    weaknesses: List[str]
    similarity_check: List[str]
    luxury_score: Dict[str, int]
    originality_score: int
    frazier_alignment_score: int
    recommendations: List[str]
    verdict: str


class LuxuryDesignAcademy:
    def __init__(self) -> None:
        self.review_categories = [
            "silhouette",
            "proportion",
            "materials",
            "craftsmanship",
            "function",
            "timelessness",
            "emotional_impact",
            "originality",
            "brand_similarity_risk",
            "frazier_alignment",
        ]

        self.ai_roles = {
            "Ajani": ["strategy", "manufacturing", "market_fit", "cost", "viability"],
            "Hermes": ["form", "materials", "construction", "ergonomics", "craftsmanship"],
            "Minerva": ["history", "culture", "symbolism", "story", "psychology"],
            "Council": ["final_review", "risks", "tradeoffs", "recommendation"],
        }

    def critique(self, concept: DesignConcept) -> DesignCritique:
        strengths: List[str] = []
        weaknesses: List[str] = []
        recommendations: List[str] = []
        similarity_check: List[str] = []

        if concept.materials:
            strengths.append("Materials were provided, allowing ATLAS to judge quality and construction direction.")
        else:
            weaknesses.append("Materials are not defined, so the design cannot yet be judged as truly premium.")
            recommendations.append("Define primary, secondary, and accent materials before approval.")

        if concept.intended_emotion:
            strengths.append("The concept includes an intended emotional direction.")
        else:
            weaknesses.append("The concept does not yet define the emotion it should create.")
            recommendations.append("Choose a target emotion such as calm, power, elegance, wonder, precision, or adventure.")

        if concept.references:
            similarity_check.append("References exist and should be checked for over-similarity before approval.")
            recommendations.append("Extract principles from references without copying their visual identity.")
        else:
            similarity_check.append("No references were provided, so similarity risk is currently unknown.")

        luxury_score = {
            "materials": 7 if concept.materials else 3,
            "craftsmanship": 5,
            "timelessness": 5,
            "emotional_impact": 7 if concept.intended_emotion else 3,
            "function": 5,
        }

        originality_score = 6 if concept.references else 5
        frazier_alignment_score = 5

        if weaknesses:
            verdict = "revise"
            first_impression = "Promising direction, but not ready for approval."
        else:
            verdict = "study further"
            first_impression = "The concept has a usable foundation and needs deeper review."

        return DesignCritique(
            first_impression=first_impression,
            strengths=strengths,
            weaknesses=weaknesses,
            similarity_check=similarity_check,
            luxury_score=luxury_score,
            originality_score=originality_score,
            frazier_alignment_score=frazier_alignment_score,
            recommendations=recommendations,
            verdict=verdict,
        )

    def council_roles(self) -> Dict[str, List[str]]:
        return self.ai_roles


def create_default_academy() -> LuxuryDesignAcademy:
    return LuxuryDesignAcademy()
