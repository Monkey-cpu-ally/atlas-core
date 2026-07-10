"""Rule-based automatic relationship builder for ATLAS Knowledge Division.

This first version is deterministic and explainable. It suggests Knowledge Bank
relationships from matched terms. Later versions can add embeddings and LLM review.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .classification import ClassificationResult, KnowledgeBankSuggestion
from .relationship_service import KnowledgeRelationshipService
from .relationships import KnowledgeNode, KnowledgeNodeType, KnowledgeRelationshipType


DEFAULT_BANK_TERMS: dict[str, set[str]] = {
    "Artificial Intelligence": {"ai", "agent", "model", "machine learning", "neural", "reasoning"},
    "Robotics": {"robot", "robotics", "actuator", "sensor", "autonomous", "manipulator"},
    "Software Engineering": {"software", "code", "api", "database", "runtime", "algorithm"},
    "Electronics": {"electronics", "circuit", "pcb", "voltage", "sensor", "microcontroller"},
    "Physics": {"physics", "force", "energy", "pressure", "motion", "thermal"},
    "Chemistry": {"chemistry", "chemical", "oxygen", "reaction", "electrolyte", "catalyst"},
    "Materials Science": {"material", "alloy", "polymer", "ceramic", "graphene", "composite"},
    "Manufacturing": {"manufacturing", "factory", "fabrication", "assembly", "production", "machining"},
    "Environmental Science": {"environment", "sustainable", "emissions", "water", "air quality", "recycling"},
    "Biology": {"biology", "biological", "cell", "organism", "tissue", "biomimicry"},
    "Business": {"business", "market", "customer", "revenue", "product", "investor"},
    "Economics": {"economics", "cost", "price", "supply", "demand", "trade"},
    "Mathematics": {"mathematics", "equation", "optimization", "probability", "statistics", "geometry"},
    "Architecture": {"architecture", "building", "structure", "space", "urban", "interior"},
    "Visual Arts": {"art", "visual", "aesthetic", "color", "illustration", "design language"},
    "Creative Writing": {"story", "character", "plot", "narrative", "worldbuilding", "script"},
}


@dataclass
class AutomaticRelationshipBuilder:
    """Classify text and create suggested Knowledge Bank relationships."""

    relationship_service: KnowledgeRelationshipService
    bank_terms: dict[str, set[str]] = field(
        default_factory=lambda: {bank: set(terms) for bank, terms in DEFAULT_BANK_TERMS.items()}
    )
    minimum_confidence: float = 0.2

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    def classify(self, title: str, text: str) -> ClassificationResult:
        normalized = self._normalize(f"{title} {text}")
        suggestions: list[KnowledgeBankSuggestion] = []

        for bank, terms in self.bank_terms.items():
            matched = sorted(term for term in terms if term in normalized)
            if not matched:
                continue

            confidence = min(0.95, 0.2 + (0.15 * len(matched)))
            if confidence < self.minimum_confidence:
                continue

            suggestions.append(
                KnowledgeBankSuggestion(
                    knowledge_bank=bank,
                    confidence=round(confidence, 2),
                    matched_terms=matched,
                    reason=f"Matched {len(matched)} domain term(s): {', '.join(matched)}",
                )
            )

        suggestions.sort(key=lambda suggestion: (-suggestion.confidence, suggestion.knowledge_bank))
        return ClassificationResult(title=title, suggestions=suggestions)

    def apply_to_node(
        self,
        source_node: KnowledgeNode,
        text: str,
        created_by: str = "automatic-relationship-builder",
    ) -> ClassificationResult:
        result = self.classify(source_node.title, text)

        existing_banks = {
            node.title: node
            for node in self.relationship_service.list_nodes(KnowledgeNodeType.KNOWLEDGE_BANK)
        }

        for suggestion in result.suggestions:
            bank_node = existing_banks.get(suggestion.knowledge_bank)
            if bank_node is None:
                bank_node = self.relationship_service.create_node(
                    title=suggestion.knowledge_bank,
                    node_type=KnowledgeNodeType.KNOWLEDGE_BANK,
                    summary="ATLAS Knowledge Bank",
                )
                existing_banks[suggestion.knowledge_bank] = bank_node

            self.relationship_service.connect(
                from_node_id=source_node.node_id,
                to_node_id=bank_node.node_id,
                relationship_type=KnowledgeRelationshipType.APPLIES_TO,
                reason=suggestion.reason,
                confidence=suggestion.confidence,
                created_by=created_by,
            )

        return result
