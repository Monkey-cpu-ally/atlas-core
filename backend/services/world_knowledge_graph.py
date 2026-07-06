"""ATLAS World Knowledge Graph.

Connects countries, regions, sources, institutions, technologies, projects,
and knowledge records into one queryable graph. V1 is registry-driven and safe:
it creates metadata relationships and does not scrape external content.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

_DB: Any = None
_NODES: Dict[str, Dict[str, Any]] = {}
_EDGES: Dict[str, Dict[str, Any]] = {}

NODE_TYPES = {"region", "country", "source", "institution", "technology", "project", "standard", "knowledge_record", "domain"}
EDGE_TYPES = {"located_in", "belongs_to_region", "covers_domain", "supports_project", "references", "related_to", "requires_standard", "owned_by_ai", "researches", "validates", "contradicts"}
AI_OWNERS = {"Ajani", "Hermes", "Minerva", "Council", "Shared"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_node(*, node_type: str, name: str, owner_ai: str = "Shared", external_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if node_type not in NODE_TYPES:
        raise ValueError(f"invalid node_type: {node_type}")
    if owner_ai not in AI_OWNERS:
        raise ValueError(f"invalid owner_ai: {owner_ai}")
    node_id = external_id or f"WKG-NODE-{str(uuid4())[:8]}"
    now = _utc_now()
    node = {
        "node_id": node_id,
        "node_type": node_type,
        "name": name,
        "owner_ai": owner_ai,
        "metadata": metadata or {},
        "created_at": now,
        "updated_at": now,
    }
    _NODES[node_id] = node
    return node


def create_edge(*, from_node_id: str, to_node_id: str, edge_type: str, confidence_score: int = 75, rationale: Optional[str] = None) -> Dict[str, Any]:
    if edge_type not in EDGE_TYPES:
        raise ValueError(f"invalid edge_type: {edge_type}")
    if from_node_id not in _NODES:
        raise ValueError(f"unknown from_node_id: {from_node_id}")
    if to_node_id not in _NODES:
        raise ValueError(f"unknown to_node_id: {to_node_id}")
    edge_id = f"WKG-EDGE-{str(uuid4())[:8]}"
    edge = {
        "edge_id": edge_id,
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "edge_type": edge_type,
        "confidence_score": max(0, min(100, int(confidence_score))),
        "rationale": rationale,
        "created_at": _utc_now(),
    }
    _EDGES[edge_id] = edge
    return edge


def get_node(node_id: str) -> Optional[Dict[str, Any]]:
    return _NODES.get(node_id)


def list_nodes(*, node_type: Optional[str] = None, owner_ai: Optional[str] = None, query: Optional[str] = None, limit: int = 500) -> List[Dict[str, Any]]:
    items = list(_NODES.values())
    if node_type:
        items = [item for item in items if item["node_type"] == node_type]
    if owner_ai:
        items = [item for item in items if item["owner_ai"].lower() == owner_ai.lower()]
    if query:
        q = query.lower()
        items = [item for item in items if q in item["name"].lower() or q in item["node_id"].lower()]
    return sorted(items, key=lambda item: (item["node_type"], item["name"]))[:limit]


def list_edges(*, node_id: Optional[str] = None, edge_type: Optional[str] = None, limit: int = 500) -> List[Dict[str, Any]]:
    items = list(_EDGES.values())
    if node_id:
        items = [item for item in items if item["from_node_id"] == node_id or item["to_node_id"] == node_id]
    if edge_type:
        items = [item for item in items if item["edge_type"] == edge_type]
    return sorted(items, key=lambda item: item["created_at"], reverse=True)[:limit]


def neighborhood(node_id: str, depth: int = 1, limit: int = 250) -> Dict[str, Any]:
    if node_id not in _NODES:
        raise ValueError(f"unknown node_id: {node_id}")
    visited = {node_id}
    frontier = {node_id}
    selected_edges: Dict[str, Dict[str, Any]] = {}
    for _ in range(max(1, min(depth, 3))):
        next_frontier = set()
        for edge in _EDGES.values():
            if edge["from_node_id"] in frontier or edge["to_node_id"] in frontier:
                selected_edges[edge["edge_id"]] = edge
                other = edge["to_node_id"] if edge["from_node_id"] in frontier else edge["from_node_id"]
                if other not in visited:
                    visited.add(other)
                    next_frontier.add(other)
        frontier = next_frontier
    nodes = [_NODES[nid] for nid in list(visited)[:limit] if nid in _NODES]
    edges = list(selected_edges.values())[:limit]
    return {"center": _NODES[node_id], "node_count": len(nodes), "edge_count": len(edges), "nodes": nodes, "edges": edges}


def graph_summary() -> Dict[str, Any]:
    by_node = {typ: 0 for typ in sorted(NODE_TYPES)}
    by_edge = {typ: 0 for typ in sorted(EDGE_TYPES)}
    for node in _NODES.values():
        by_node[node["node_type"]] += 1
    for edge in _EDGES.values():
        by_edge[edge["edge_type"]] += 1
    return {
        "title": "ATLAS World Knowledge Graph Summary",
        "generated_at": _utc_now(),
        "node_count": len(_NODES),
        "edge_count": len(_EDGES),
        "nodes_by_type": by_node,
        "edges_by_type": by_edge,
    }


def seed_foundation_graph() -> Dict[str, Any]:
    reset_in_memory_state()
    for region in ["North America", "South America", "Europe", "Africa", "Asia", "Oceania", "International", "Personal"]:
        create_node(node_type="region", name=region, external_id=f"region:{_slug(region)}")
    countries = {
        "United States": "North America", "Germany": "Europe", "Switzerland": "Europe", "Japan": "Asia",
        "South Korea": "Asia", "Singapore": "Asia", "India": "Asia", "Australia": "Oceania",
        "Brazil": "South America", "South Africa": "Africa", "International": "International", "Personal": "Personal",
    }
    for country, region in countries.items():
        c = create_node(node_type="country", name=country, external_id=f"country:{_slug(country)}")
        create_edge(from_node_id=c["node_id"], to_node_id=f"region:{_slug(region)}", edge_type="belongs_to_region", rationale="Country is grouped under this ATLAS world region.")
    domains = ["Robotics", "AI", "Aerospace", "Medicine", "Materials", "Energy", "Manufacturing", "Agriculture", "Environmental Science", "Software Engineering", "Standards"]
    for domain in domains:
        create_node(node_type="domain", name=domain, external_id=f"domain:{_slug(domain)}")
    source_map = [
        ("NASA", "United States", ["Aerospace", "Robotics"]), ("NIST", "United States", ["Standards", "Materials"]),
        ("NIH", "United States", ["Medicine"]), ("Fraunhofer Society", "Germany", ["Manufacturing", "Materials"]),
        ("ETH Zurich", "Switzerland", ["Robotics", "AI"]), ("JAXA", "Japan", ["Aerospace", "Robotics"]),
        ("RIKEN", "Japan", ["AI", "Materials"]), ("KAIST", "South Korea", ["Robotics", "AI"]),
        ("A*STAR", "Singapore", ["Materials", "Manufacturing"]), ("ISRO", "India", ["Aerospace"]),
        ("CSIRO", "Australia", ["Agriculture", "Environmental Science"]), ("EMBRAPA", "Brazil", ["Agriculture"]),
        ("CSIR South Africa", "South Africa", ["Materials", "Environmental Science"]), ("ISO", "International", ["Standards"]),
        ("IEEE", "International", ["Standards", "Software Engineering", "AI"]), ("Frazier GitHub Archive", "Personal", ["Software Engineering"]),
    ]
    for name, country, domains_for_source in source_map:
        src = create_node(node_type="source", name=name, owner_ai="Council", external_id=f"source:{_slug(name)}", metadata={"country": country})
        create_edge(from_node_id=src["node_id"], to_node_id=f"country:{_slug(country)}", edge_type="located_in")
        for domain in domains_for_source:
            create_edge(from_node_id=src["node_id"], to_node_id=f"domain:{_slug(domain)}", edge_type="covers_domain")
    projects = [("Weaver", "project:weaver", ["Robotics", "Manufacturing"]), ("Power Cell", "project:power_cell", ["Energy", "Materials"]), ("Minerva Plant Library", "project:minerva_plant_library", ["Agriculture", "Environmental Science"])]
    for name, project_id, project_domains in projects:
        p = create_node(node_type="project", name=name, owner_ai="Shared", external_id=project_id)
        for domain in project_domains:
            create_edge(from_node_id=p["node_id"], to_node_id=f"domain:{_slug(domain)}", edge_type="covers_domain")
    return {"created_nodes": len(_NODES), "created_edges": len(_EDGES), "summary": graph_summary()}


def reset_in_memory_state() -> None:
    _NODES.clear(); _EDGES.clear()


async def persist_all() -> None:
    if _DB is None:
        return
    for item in _NODES.values():
        await _DB.world_knowledge_nodes.update_one({"node_id": item["node_id"]}, {"$set": item}, upsert=True)
    for item in _EDGES.values():
        await _DB.world_knowledge_edges.update_one({"edge_id": item["edge_id"]}, {"$set": item}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"world_knowledge_nodes": 0, "world_knowledge_edges": 0}
    nodes = await _DB.world_knowledge_nodes.find({}, {"_id": 0}).to_list(50000)
    edges = await _DB.world_knowledge_edges.find({}, {"_id": 0}).to_list(100000)
    reset_in_memory_state()
    for item in nodes:
        _NODES[item["node_id"]] = item
    for item in edges:
        _EDGES[item["edge_id"]] = item
    return {"world_knowledge_nodes": len(_NODES), "world_knowledge_edges": len(_EDGES)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.world_knowledge_nodes.create_index("node_id", unique=True)
    await _DB.world_knowledge_nodes.create_index("node_type")
    await _DB.world_knowledge_edges.create_index("edge_id", unique=True)
    await _DB.world_knowledge_edges.create_index("from_node_id")
    await _DB.world_knowledge_edges.create_index("to_node_id")
    await _DB.world_knowledge_edges.create_index("edge_type")


def _slug(value: str) -> str:
    return "-".join(value.lower().replace("&", "and").replace("/", " ").replace("*", "star").split())
