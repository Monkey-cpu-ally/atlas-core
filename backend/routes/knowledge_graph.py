"""ATLAS Knowledge Graph routes."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import knowledge_graph_engine as graph

router = APIRouter(prefix="/api/knowledge-graph", tags=["ATLAS Knowledge Graph"])


class NodeRequest(BaseModel):
    label: str = Field(min_length=1, max_length=240)
    node_type: str = "concept"
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    node_id: Optional[str] = None


class EdgeRequest(BaseModel):
    source_node_id: str
    target_node_id: str
    edge_type: str = "related_to"
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    edge_id: Optional[str] = None


@router.get("/health")
async def health():
    return {"status": "ok", "engine": "knowledge_graph_engine", "stats": graph.stats()}


@router.get("/stats")
async def stats():
    return graph.stats()


@router.post("/nodes")
async def create_node(req: NodeRequest):
    try:
        node = graph.upsert_node(**req.model_dump())
        await graph.persist_node(node)
        return node
    except graph.KnowledgeGraphError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/nodes")
async def list_nodes(
    node_type: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = Query(None, description="Search label/description"),
):
    try:
        items = graph.list_nodes(node_type=node_type, tag=tag, q=q)
        return {"count": len(items), "items": items}
    except graph.KnowledgeGraphError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/nodes/{node_id}")
async def get_node(node_id: str):
    node = graph.get_node(node_id)
    if not node:
        raise HTTPException(404, f"node not found: {node_id}")
    return node


@router.post("/edges")
async def create_edge(req: EdgeRequest):
    try:
        edge = graph.create_edge(**req.model_dump())
        await graph.persist_edge(edge)
        return edge
    except graph.KnowledgeGraphError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/edges")
async def list_edges(node_id: Optional[str] = None, edge_type: Optional[str] = None):
    try:
        items = graph.list_edges(node_id=node_id, edge_type=edge_type)
        return {"count": len(items), "items": items}
    except graph.KnowledgeGraphError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/neighborhood/{node_id}")
async def neighborhood(node_id: str, depth: int = Query(1, ge=1, le=3)):
    try:
        return graph.neighborhood(node_id, depth=depth)
    except graph.KnowledgeGraphError as exc:
        raise HTTPException(404, str(exc)) from exc
