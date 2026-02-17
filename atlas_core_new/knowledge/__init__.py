"""
ATLAS Knowledge System
Defines how the AIs access, use, and reconstruct knowledge.
Pattern-based learning, not memorization.
"""
from .philosophy import KNOWLEDGE_PHILOSOPHY, KNOWLEDGE_PRINCIPLES
from .sources import KNOWLEDGE_SOURCES, get_sources_for_persona
from .boundaries import KNOWLEDGE_BOUNDARIES, ABSOLUTE_LIMITS
from .custom_packs import CustomKnowledgePack, knowledge_pack_registry, get_context_from_packs

__all__ = [
    'KNOWLEDGE_PHILOSOPHY',
    'KNOWLEDGE_PRINCIPLES',
    'KNOWLEDGE_SOURCES',
    'get_sources_for_persona',
    'KNOWLEDGE_BOUNDARIES',
    'ABSOLUTE_LIMITS',
    'CustomKnowledgePack',
    'knowledge_pack_registry',
    'get_context_from_packs'
]
