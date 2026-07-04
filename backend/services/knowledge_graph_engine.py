"""ATLAS Knowledge Graph Engine.

Connects projects, discoveries, sources, subjects, blueprints, and AI owners into
queryable relationships. V1 is deterministic in-memory with optional MongoDB
persistence, matching the Research Lab pattern.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

VALID_NODE_TYPES = {
    "concept", "project", "source", "subject", "ai", "discovery", "mission",
    "blueprint", "bank", "material", "technology", "risk", "decision"
}

VALID_EDGE_TYPES = {
    "related_to", "supports", "contradicts", "belongs_to", "owned_by", "uses",
    "improves", "depends_on", "cites", "created_from", "reviewed_by", "affects"
}

_NODES: Dict[str, Dict[str, Any]] = {}
_EDGES: Dict[str, Dict[str, Any]] = {}
_DB: Any = None


class KnowledgeGraphError(RuntimeError):
    """Raised when a graph operation is invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_node(
    *,
    label: str,
    node_type: str = "concept",
    description: str = "",
    tags: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None,
    node_id: Optional[str] = None,
) -> Dict[str, Any]:
    if node_type not in VALID_NODE_TYPES:
        raise KnowledgeGraphError(f"invalid node_type: {node_type}")
    nid = node_id or f"{node_type}-{_slug(label)}-{str(uuid4())[:8]}"
    node = {
        "node_id": nid,
        "label": label,
        "node_type": node_type,
        "description": description,
        "tags": tags or [],
        "properties": properties or {},
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _NODES[nid] = node
    return node


def upsert_node(**kwargs: Any) -> Dict[str, Any]:
    node_id = kwargs.get("node_id")
    if node_id and node_id in _NODES:
        node = _NODES[node_id]
        for key in ("label", "node_type", "description", "tags", "properties"):
            if key in kwargs and kwargs[key] is not None:
                node[key] = kwargs[key]
        node["updated_at"] = _utc_now()
        return node
    return create_node(**kwargs)


def get_node(node_id: str) -> Optional[Dict[str, Any]]:
    return _NODES.get(node_id)


def list_nodes(node_type: Optional[str] = None, tag: Optional[str] = None, q: Optional[str] = None) -> List[Dict[str, Any]]:
    if node_type and node_type not in VALID_NODE_TYPES:
        raise KnowledgeGraphError(f"invalid node_type: {node_type}")
    nodes = list(_NODES.values())
    if node_type:
        nodes = [n for n in nodes if n["node_type"] == node_type]
    if tag:
        nodes = [n for n in nodes if tag in n.get("tags", [])]
    if q:
        query = q.lower()
        nodes = [n for n in nodes if query in n.get("label", "").lower() or query in n.get("description", "").lower()]
    return sorted(nodes, key=lambda n: n["updated_at"], reverse=True)


def create_edge(
    *,
    source_node_id: str,
    target_node_id: str,
    edge_type: str = "related_to",
    weight: float = 1.0,
    evidence: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None,
    edge_id: Optional[str] = None,
) -> Dict[str, Any]:
    if edge_type not in VALID_EDGE_TYPES:
        raise KnowledgeGraphError(f"invalid edge_type: {edge_type}")
    if source_node_id not in _NODES:
        raise KnowledgeGraphError(f"unknown source_node_id: {source_node_id}")
    if target_node_id not in _NODES:
        raise KnowledgeGraphError(f"unknown target_node_id: {target_node_id}")

    eid = edge_id or f"edge-{str(uuid4())[:10]}"
    edge = {
        "edge_id": eid,
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "edge_type": edge_type,
        "weight": max(0.0, min(1.0, float(weight))),
        "evidence": evidence or [],
        "properties": properties or {},
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _EDGES[eid] = edge
    return edge


def list_edges(node_id: Optional[str] = None, edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
    if edge_type and edge_type not in VALID_EDGE_TYPES:
        raise KnowledgeGraphError(f"invalid edge_type: {edge_type}")
    edges = list(_EDGES.values())
    if node_id:
        edges = [e for e in edges if e["source_node_id"] == node_id or e["target_node_id"] == node_id]
    if edge_type:
        edges = [e for e in edges if e["edge_type"] == edge_type]
    return sorted(edges, key=lambda e: e["updated_at"], reverse=True)


def neighborhood(node_id: str, depth: int = 1) -> Dict[str, Any]:
    if node_id not in _NODES:
        raise KnowledgeGraphError(f"unknown node_id: {node_id}")
    depth = max(1, min(3, int(depth)))
    seen_nodes = {node_id}
    frontier = {node_id}
    found_edges: Dict[str, Dict[str, Any]] = {}

    for _ in range(depth):
        next_frontier = set()
        for edge in _EDGES.values():
            s = edge["source_node_id"]
            t = edge["target_node_id"]
            if s in frontier or t in frontier:
                found_edges[edge["edge_id"]] = edge
                if s not in seen_nodes:
                    next_frontier.add(s)
                if t not in seen_nodes:
                    next_frontier.add(t)
                seen_nodes.add(s)
                seen_nodes.add(t)
        frontier = next_frontier
        if not frontier:
            break

    return {
        "center": _NODES[node_id],
        "nodes": [_NODES[nid] for nid in seen_nodes],
        "edges": list(found_edges.values()),
        "depth": depth,
    }


def stats() -> Dict[str, Any]:
    by_type: Dict[str, int] = {}
    for node in _NODES.values():
        by_type[node["node_type"]] = by_type.get(node["node_type"], 0) + 1
    by_edge_type: Dict[str, int] = {}
    for edge in _EDGES.values():
        by_edge_type[edge["edge_type"]] = by_edge_type.get(edge["edge_type"], 0) + 1
    return {
        "nodes": len(_NODES),
        "edges": len(_EDGES),
        "by_node_type": by_type,
        "by_edge_type": by_edge_type,
        "persistence_enabled": persistence_enabled(),
    }


async def persist_node(node: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.knowledge_graph_nodes.update_one({"node_id": node["node_id"]}, {"$set": node}, upsert=True)


async def persist_edge(edge: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.knowledge_graph_edges.update_one({"edge_id": edge["edge_id"]}, {"$set": edge}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"nodes": 0, "edges": 0}
    nodes = await _DB.knowledge_graph_nodes.find({}, {"_id": 0}).to_list(10000)
    edges = await _DB.knowledge_graph_edges.find({}, {"_id": 0}).to_list(20000)
    _NODES.clear()
    _EDGES.clear()
    for node in nodes:
        _NODES[node["node_id"]] = node
    for edge in edges:
        _EDGES[edge["edge_id"]] = edge
    return {"nodes": len(_NODES), "edges": len(_EDGES)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.knowledge_graph_nodes.create_index("node_id", unique=True)
    await _DB.knowledge_graph_nodes.create_index([("node_type", 1), ("label", 1)])
    await _DB.knowledge_graph_nodes.create_index("tags")
    await _DB.knowledge_graph_edges.create_index("edge_id", unique=True)
    await _DB.knowledge_graph_edges.create_index([("source_node_id", 1), ("target_node_id", 1)])
    await _DB.knowledge_graph_edges.create_index("edge_type")


def reset_in_memory_state() -> None:
    _NODES.clear()
    _EDGES.clear()
