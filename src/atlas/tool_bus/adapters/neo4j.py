"""Neo4j adapter scaffold for ATLAS Tool Bus."""

from __future__ import annotations

from ..contracts import ToolCapability, ToolSafetyLevel
from .base import PlaceholderToolAdapter


class Neo4jAdapter(PlaceholderToolAdapter):
    """Placeholder adapter for future graph memory integration."""

    def __init__(self) -> None:
        super().__init__(
            name="neo4j",
            capabilities=[
                ToolCapability(
                    name="query_graph",
                    description="Query ATLAS graph memory when Neo4j is configured.",
                    safety_level=ToolSafetyLevel.READ_ONLY,
                    enabled_by_default=False,
                ),
                ToolCapability(
                    name="write_graph_event",
                    description="Write a verified ATLAS concept, relationship, or project event into graph memory.",
                    safety_level=ToolSafetyLevel.WRITE_LOCAL,
                    enabled_by_default=False,
                ),
            ],
        )
