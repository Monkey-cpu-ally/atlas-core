from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FashionConcept:
    name: str
    garment_type: str
    description: str
    silhouette: str = ""
    fabrics: List[str] = field(default_factory=list)
    hardware: List[str] = field(default_factory=list)
    intended_use: str = ""
    references: List[str] = field(default_factory=list)


@dataclass
class FashionCritique:
    first_impression: str
    silhouette_review: str
    fit_and_movement_review: str
    fabric_review: str
    construction_review: str
    styling_review: str
    similarity_check: List[str]
    scores: Dict[str, int]
    recommendations: List[str]
    verdict: str


class FashionAcademy:
    def critique(self, concept: FashionConcept) -> FashionCritique:
        recommendations: List[str] = []
        similarity_check: List[str] = []

        if concept.silhouette:
            silhouette_review = "Silhouette direction is defined and can be judged for balance and identity."
            silhouette_score = 7
        else:
            silhouette_review = "Silhouette is not defined, so the garment lacks a strong first-read identity."
            silhouette_score = 3
            recommendations.append("Define the garment silhouette before developing details.")

        if concept.intended_use:
            fit_review = "Intended use is defined, so fit and movement can be evaluated against a real context."
            function_score = 7
        else:
            fit_review = "Intended use is missing, so comfort, movement, and practicality are unclear."
            function_score = 4
            recommendations.append("Define where and how this garment will be worn.")

        if concept.fabrics:
            fabric_review = "Fabric direction is present and should be tested for drape, structure, aging, and comfort."
            material_score = 7
        else:
            fabric_review = "Fabric choices are missing, so the garment cannot yet be evaluated for luxury or construction quality."
            material_score = 3
            recommendations.append("Choose primary fabric, support fabric, lining, and trim materials.")

        if concept.hardware:
            construction_review = "Hardware is included and should be checked for weight, durability, placement, and originality."
        else:
            construction_review = "Hardware is not specified. This may be fine for minimal garments, but closures and reinforcement still need review."

        if concept.references:
            similarity_check.append("References are present. ATLAS should check silhouette, seams, hardware, and styling for over-similarity.")
            recommendations.append("Extract principles from references while changing enough structure to protect originality.")
        else:
            similarity_check.append("No references provided, so similarity risk is unknown.")

        styling_review = "Styling should be evaluated with footwear, accessories, color palette, season, and lifestyle context."

        scores = {
            "silhouette": silhouette_score,
            "materials": material_score,
            "function": function_score,
            "construction": 5,
            "originality": 6 if concept.references else 5,
            "luxury_read": round((silhouette_score + material_score + function_score) / 3),
        }

        if min(scores.values()) < 5:
            verdict = "revise"
            first_impression = "The fashion concept has potential but needs clearer design decisions before approval."
        else:
            verdict = "study further"
            first_impression = "The fashion concept is usable for deeper critique and refinement."

        return FashionCritique(
            first_impression=first_impression,
            silhouette_review=silhouette_review,
            fit_and_movement_review=fit_review,
            fabric_review=fabric_review,
            construction_review=construction_review,
            styling_review=styling_review,
            similarity_check=similarity_check,
            scores=scores,
            recommendations=recommendations,
            verdict=verdict,
        )


def create_fashion_academy() -> FashionAcademy:
    return FashionAcademy()
