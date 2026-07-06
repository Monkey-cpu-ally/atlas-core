"""ATLAS World Knowledge Graph routes."""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import world_knowledge_graph as wkg

router = APIRouter(prefix="/api/world-knowledge-graph", tags=["ATLAS World Knowledge Graph"])


class NodeRequest(BaseModel):
    node_type: str
    name: str = Field(min_length=2, max_length=250)
    owner_ai: str = "Shared"
    external_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EdgeRequest(BaseModel):
    from_node_id: str
    to_node_id: str
    edge_type: str
    confidence_score: int = Field(default=75, ge=0, le=100)
    rationale: Optional[str] = None


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "world_knowledge_graph",
        "persistence_enabled": wkg.persistence_enabled(),
        "node_count": wkg.graph_summary()["node_count"],
    }


@router.post("/seed")
async def seed_foundation_graph():
    result = wkg.seed_foundation_graph()
    await wkg.persist_all()
    return result


@router.get("/summary")
async def summary():
    return wkg.graph_summary()


@router.post("/nodes")
async def create_node(req: NodeRequest):
    try:
        node = wkg.create_node(**req.model_dump())
        await wkg.persist_all()
        return node
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/nodes")
async def list_nodes(node_type: Optional[str] = None, owner_ai: Optional[str] = None, query: Optional[str] = None, limit: int = 500):
    return {"count": len(wkg.list_nodes(node_type=node_type, owner_ai=owner_ai, query=query, limit=limit)), "items": wkg.list_nodes(node_type=node_type, owner_ai=owner_ai, query=query, limit=limit)}


@router.get("/nodes/{node_id:path}")
async def get_node(node_id: str):
    node = wkg.get_node(node_id)
    if not node:
        raise HTTPException(404, f"node not found: {node_id}")
    return node


@router.post("/edges")
async def create_edge(req: EdgeRequest):
    try:
        edge = wkg.create_edge(**req.model_dump())
        await wkg.persist_all()
        return edge
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/edges")
async def list_edges(node_id: Optional[str] = None, edge_type: Optional[str] = None, limit: int = 500):
    items = wkg.list_edges(node_id=node_id, edge_type=edge_type, limit=limit)
    return {"count": len(items), "items": items}


@router.get("/neighborhood/{node_id:path}")
async def neighborhood(node_id: str, depth: int = 1, limit: int = 250):
    try:
        return wkg.neighborhood(node_id=node_id, depth=depth, limit=limit)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
