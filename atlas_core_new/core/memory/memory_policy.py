"""
atlas_core/core/memory/memory_policy.py

Memory extraction and policy for gating what gets stored.
"""

from dataclasses import dataclass
from typing import List

from .memory_models import MemoryItem


@dataclass
class MemoryPolicy:
    allow_personal_data: bool = False
    min_confidence: float = 0.70


class MemoryExtractor:
    """
    Very simple extractor: you can replace with LLM-driven extraction later.
    """
    def extract(self, text: str) -> List[MemoryItem]:
        lowered = text.lower()
        if "remember that" in lowered:
            payload = text.split("remember that", 1)[1].strip()
            return [MemoryItem(key="note", value=payload, confidence=0.75)]
        return []
