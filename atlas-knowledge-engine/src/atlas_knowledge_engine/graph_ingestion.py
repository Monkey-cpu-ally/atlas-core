"""Learning-pipeline hook that creates traceable graph relationships."""

from __future__ import annotations

from collections.abc import Iterable

from .graph_models import GraphEdge, GraphNode
from .knowledge_graph import KnowledgeGraph
from .learning_adapter import ExtractedContent


class GraphIngestionHook:
    """Convert normalized learned content into source, creator, and topic nodes."""

    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph

    @staticmethod
    def _string_items(value: object) -> tuple[str, ...]:
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, Iterable):
            return ()
        cleaned = []
        for item in value:
            text = " ".join(str(item).split()).strip()
            if text and text not in cleaned:
                cleaned.append(text)
        return tuple(cleaned)

    def __call__(self, content: ExtractedContent) -> None:
        source = self.graph.add_node(
            GraphNode(
                node_type="source",
                name=f"{content.source_type}:{content.source_id}",
                description=content.title,
                tags=(content.source_type,),
                metadata={
                    "title": content.title,
                    "canonical_url": content.canonical_url,
                    "creator": content.creator,
                    **dict(content.metadata),
                },
            )
        )

        if content.creator and content.creator.strip():
            creator = self.graph.add_node(
                GraphNode(node_type="creator", name=content.creator.strip())
            )
            self.graph.add_edge(
                GraphEdge(source_id=creator.node_id, target_id=source.node_id, relation="created")
            )

        subjects = self._string_items(content.metadata.get("subjects"))
        topics = self._string_items(content.metadata.get("topics"))
        projects = self._string_items(content.metadata.get("projects"))

        for subject_name in subjects:
            subject = self.graph.add_node(GraphNode(node_type="subject", name=subject_name))
            self.graph.add_edge(
                GraphEdge(source_id=source.node_id, target_id=subject.node_id, relation="belongs_to")
            )

        for topic_name in topics:
            topic = self.graph.add_node(GraphNode(node_type="concept", name=topic_name))
            self.graph.add_edge(
                GraphEdge(source_id=source.node_id, target_id=topic.node_id, relation="discusses")
            )

        for project_name in projects:
            project = self.graph.add_node(GraphNode(node_type="project", name=project_name))
            self.graph.add_edge(
                GraphEdge(source_id=source.node_id, target_id=project.node_id, relation="supports")
            )

    def health(self) -> dict[str, object]:
        return {"status": "healthy", "graph": self.graph.health()}
