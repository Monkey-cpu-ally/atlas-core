"""
atlas_core/core/memory/memory_models.py

Memory data models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class MemoryItem:
    key: str
    value: str
    confidence: float = 0.75
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MemoryEntry:
    role: str
    content: str
    meta: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MemorySnapshot:
    items: List[MemoryItem] = field(default_factory=list)
    transcript: List[MemoryEntry] = field(default_factory=list)
