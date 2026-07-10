"""Classification models for automatic ATLAS knowledge routing."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class KnowledgeBankSuggestion:
    """A suggested Knowledge Bank assignment with traceable evidence."""

    knowledge_bank: str
    confidence: float
    matched_terms: list[str] = field(default_factory=list)
    reason: str = ""


@dataclass(slots=True)
class ClassificationResult:
    """Result returned by the automatic Knowledge Bank classifier."""

    title: str
    suggestions: list[KnowledgeBankSuggestion]

    def top(self, limit: int = 5) -> list[KnowledgeBankSuggestion]:
        if limit < 1:
            return []
        return self.suggestions[:limit]
