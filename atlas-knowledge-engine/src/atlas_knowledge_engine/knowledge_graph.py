"""Thread-safe in-memory knowledge graph for ATLAS."""

from __future__ import annotations

from collections import defaultdict, deque
from threading import RLock
from typing import Any

from .graph_models import GraphEdge, GraphNode


class KnowledgeGraph:
    """Store typed nodes and directed relationships behind a replaceable API."""

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[str, GraphEdge] = {}
        self._name_index: dict[tuple[str, str], str] = {}
        self._outgoing: dict[str, set[str]] = defaultdict(set)
        self._incoming: dict[str, set[str]] = defaultdict(set)
        self._edge_index: dict[tuple[str, str, str], str] = {}
        self._lock = RLock()

    @staticmethod
    def _node_key(node_type: str, name: str) -> tuple[str, str]:
        return node_type.strip().lower(), " ".join(name.lower().split())

    def add_node(self, node: GraphNode, *, merge: bool = True) -> GraphNode:
        key = self._node_key(node.node_type, node.name)
        with self._lock:
            existing_id = self._name_index.get(key)
            if existing_id is not None:
                if not merge:
                    raise KeyError(f"graph node already exists: {key[0]}:{key[1]}")
                existing = self._nodes[existing_id]
                combined = GraphNode(
                    node_type=existing.node_type,
                    name=existing.name,
                    description=node.description or existing.description,
                    node_id=existing.node_id,
                    aliases=tuple(sorted(set(existing.aliases) | set(node.aliases))),
                    tags=tuple(sorted(set(existing.tags) | set(node.tags))),
                    metadata={**existing.metadata, **node.metadata},
                    created_at=existing.created_at,
                )
                self._nodes[existing_id] = combined
                return combined
            self._nodes[node.node_id] = node
            self._name_index[key] = node.node_id
            return node

    def get_node(self, node_id: str) -> GraphNode:
        with self._lock:
            try:
                return self._nodes[node_id]
            except KeyError as exc:
                raise KeyError(f"graph node not found: {node_id}") from exc

    def find_node(self, node_type: str, name: str) -> GraphNode | None:
        key = self._node_key(node_type, name)
        with self._lock:
            node_id = self._name_index.get(key)
            return self._nodes.get(node_id) if node_id else None

    def add_edge(self, edge: GraphEdge, *, merge: bool = True) -> GraphEdge:
        relation = edge.relation.strip().lower()
        key = (edge.source_id, relation, edge.target_id)
        with self._lock:
            if edge.source_id not in self._nodes or edge.target_id not in self._nodes:
                raise KeyError("both graph edge endpoints must exist")
            existing_id = self._edge_index.get(key)
            if existing_id is not None:
                if not merge:
                    raise KeyError("graph edge already exists")
                existing = self._edges[existing_id]
                combined = GraphEdge(
                    source_id=existing.source_id,
                    target_id=existing.target_id,
                    relation=existing.relation,
                    edge_id=existing.edge_id,
                    weight=max(existing.weight, edge.weight),
                    metadata={**existing.metadata, **edge.metadata},
                    created_at=existing.created_at,
                )
                self._edges[existing_id] = combined
                return combined
            normalized = GraphEdge(
                source_id=edge.source_id,
                target_id=edge.target_id,
                relation=relation,
                edge_id=edge.edge_id,
                weight=edge.weight,
                metadata=dict(edge.metadata),
                created_at=edge.created_at,
            )
            self._edges[normalized.edge_id] = normalized
            self._edge_index[key] = normalized.edge_id
            self._outgoing[normalized.source_id].add(normalized.edge_id)
            self._incoming[normalized.target_id].add(normalized.edge_id)
            return normalized

    def neighbors(self, node_id: str, *, relation: str | None = None) -> tuple[GraphNode, ...]:
        with self._lock:
            if node_id not in self._nodes:
                raise KeyError(f"graph node not found: {node_id}")
            relation_filter = relation.strip().lower() if relation else None
            neighbor_ids: set[str] = set()
            for edge_id in self._outgoing.get(node_id, ()):
                edge = self._edges[edge_id]
                if relation_filter is None or edge.relation == relation_filter:
                    neighbor_ids.add(edge.target_id)
            for edge_id in self._incoming.get(node_id, ()):
                edge = self._edges[edge_id]
                if relation_filter is None or edge.relation == relation_filter:
                    neighbor_ids.add(edge.source_id)
            return tuple(self._nodes[item] for item in sorted(neighbor_ids))

    def path(self, start_id: str, target_id: str, *, max_depth: int = 6) -> tuple[str, ...] | None:
        if max_depth < 1:
            raise ValueError("max_depth must be at least 1")
        with self._lock:
            if start_id not in self._nodes or target_id not in self._nodes:
                return None
            queue: deque[tuple[str, tuple[str, ...]]] = deque([(start_id, (start_id,))])
            visited = {start_id}
            while queue:
                current, trail = queue.popleft()
                if len(trail) - 1 >= max_depth:
                    continue
                edge_ids = self._outgoing.get(current, set()) | self._incoming.get(current, set())
                for edge_id in edge_ids:
                    edge = self._edges[edge_id]
                    next_id = edge.target_id if edge.source_id == current else edge.source_id
                    if next_id == target_id:
                        return (*trail, next_id)
                    if next_id not in visited:
                        visited.add(next_id)
                        queue.append((next_id, (*trail, next_id)))
            return None

    def nodes(self) -> tuple[GraphNode, ...]:
        with self._lock:
            return tuple(self._nodes[key] for key in sorted(self._nodes))

    def edges(self) -> tuple[GraphEdge, ...]:
        with self._lock:
            return tuple(self._edges[key] for key in sorted(self._edges))

    def health(self) -> dict[str, Any]:
        with self._lock:
            return {
                "status": "healthy",
                "nodes": len(self._nodes),
                "edges": len(self._edges),
                "storage": "memory",
            }
