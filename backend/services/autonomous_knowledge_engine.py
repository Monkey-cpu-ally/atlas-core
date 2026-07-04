"""ATLAS Autonomous Knowledge Engine.

Connects World Knowledge sources, Research Labs, and the Knowledge Graph.
V1 is safe and deterministic: it creates knowledge missions from user intent,
selects approved sources, assigns them to the right AI, and can draft graph
nodes/edges without performing autonomous web crawling.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from services import world_knowledge_connector as sources
from services import research_lab_engine as labs
from services import knowledge_graph_engine as graph

VALID_STATUSES = {"planned", "queued", "running", "completed", "failed", "council_review"}
_ENGINE_JOBS: Dict[str, Dict[str, Any]] = {}
_DB: Any = None


class AutonomousKnowledgeError(RuntimeError):
    """Raised when an autonomous knowledge operation is invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def _score_source(source: Dict[str, Any], subject_tags: List[str], preferred_ai: Optional[str]) -> int:
    score = int(source.get("trust_score") or 0)
    source_subjects = {str(s).lower() for s in source.get("subjects", [])}
    requested_subjects = {str(s).lower() for s in subject_tags}
    score += 8 * len(source_subjects.intersection(requested_subjects))
    if preferred_ai and str(source.get("ai_owner", "")).lower() == preferred_ai.lower():
        score += 12
    if source.get("auto_sync"):
        score += 3
    return score


def choose_sources(
    *,
    subject_tags: Optional[List[str]] = None,
    preferred_ai: Optional[str] = None,
    limit: int = 6,
    min_trust_score: int = 70,
) -> List[Dict[str, Any]]:
    """Choose approved sources for a knowledge mission."""
    subject_tags = subject_tags or []
    candidates = sources.list_sources(ai_owner=preferred_ai) if preferred_ai else sources.list_sources()
    ranked = []
    for source in candidates:
        if int(source.get("trust_score") or 0) < min_trust_score:
            continue
        if subject_tags:
            source_subjects = {str(s).lower() for s in source.get("subjects", [])}
            requested_subjects = {str(s).lower() for s in subject_tags}
            if not source_subjects.intersection(requested_subjects):
                continue
        ranked.append((_score_source(source, subject_tags, preferred_ai), source))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [source for _, source in ranked[: max(1, min(limit, 20))]]


def create_knowledge_mission(
    *,
    title: str,
    goal: str,
    owner_ai: str,
    subject_tags: Optional[List[str]] = None,
    related_projects: Optional[List[str]] = None,
    priority: str = "normal",
    source_limit: int = 6,
    council_review_required: bool = True,
) -> Dict[str, Any]:
    """Create an autonomous knowledge job and matching Research Lab mission."""
    selected_sources = choose_sources(
        subject_tags=subject_tags or [],
        preferred_ai=owner_ai if owner_ai != "Council" else None,
        limit=source_limit,
    )
    if not selected_sources:
        raise AutonomousKnowledgeError("no approved sources matched this mission")

    source_ids = [source["id"] for source in selected_sources]
    mission = labs.create_mission(
        title=title,
        owner_ai=owner_ai,
        goal=goal,
        source_ids=source_ids,
        subject_tags=subject_tags or [],
        related_projects=related_projects or [],
        priority=priority,
        council_review_required=council_review_required,
    )

    job_id = f"AKE-{str(uuid4())[:8]}"
    job = {
        "job_id": job_id,
        "status": "queued",
        "title": title,
        "goal": goal,
        "owner_ai": mission["owner_ai"],
        "mission_id": mission["mission_id"],
        "source_ids": source_ids,
        "source_count": len(source_ids),
        "subject_tags": subject_tags or [],
        "related_projects": related_projects or [],
        "priority": priority,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
        "next_action": "Run source previews, draft discovery, then submit to Council review.",
    }
    _ENGINE_JOBS[job_id] = job
    return {"job": job, "mission": mission, "sources": selected_sources}


def list_jobs(owner_ai: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    if status and status not in VALID_STATUSES:
        raise AutonomousKnowledgeError(f"invalid status: {status}")
    jobs = list(_ENGINE_JOBS.values())
    if owner_ai:
        jobs = [job for job in jobs if job["owner_ai"].lower() == owner_ai.lower()]
    if status:
        jobs = [job for job in jobs if job["status"] == status]
    return sorted(jobs, key=lambda job: job["updated_at"], reverse=True)


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    return _ENGINE_JOBS.get(job_id)


def mark_job_status(job_id: str, status: str) -> Dict[str, Any]:
    if status not in VALID_STATUSES:
        raise AutonomousKnowledgeError(f"invalid status: {status}")
    job = get_job(job_id)
    if not job:
        raise AutonomousKnowledgeError(f"unknown job_id: {job_id}")
    job["status"] = status
    job["updated_at"] = _utc_now()
    return job


def draft_graph_from_mission(job_id: str) -> Dict[str, Any]:
    """Create starter Knowledge Graph nodes/edges for a mission.

    This is not final truth. It creates traceable scaffolding so discoveries,
    sources, projects, and subjects can connect as the mission matures.
    """
    job = get_job(job_id)
    if not job:
        raise AutonomousKnowledgeError(f"unknown job_id: {job_id}")

    mission_node = graph.upsert_node(
        node_id=f"mission:{job['mission_id']}",
        label=job["title"],
        node_type="mission",
        description=job["goal"],
        tags=job.get("subject_tags", []),
        properties={"owner_ai": job["owner_ai"], "job_id": job_id},
    )
    created_nodes = [mission_node]
    created_edges = []

    ai_node = graph.upsert_node(
        node_id=f"ai:{job['owner_ai'].lower()}",
        label=job["owner_ai"],
        node_type="ai",
        description="ATLAS AI research owner",
        tags=["atlas_ai"],
        properties={},
    )
    created_nodes.append(ai_node)
    created_edges.append(graph.create_edge(
        source_node_id=mission_node["node_id"],
        target_node_id=ai_node["node_id"],
        edge_type="owned_by",
        evidence=[f"Autonomous Knowledge Engine job {job_id}"],
    ))

    for source_id in job.get("source_ids", []):
        source = sources.get_source(source_id)
        if not source:
            continue
        source_node = graph.upsert_node(
            node_id=f"source:{source_id}",
            label=source.get("name", source_id),
            node_type="source",
            description=f"Approved World Knowledge source from {source.get('country')}",
            tags=source.get("subjects", []),
            properties={"trust_score": source.get("trust_score"), "trust_tier": source.get("trust_tier"), "url": source.get("url")},
        )
        created_nodes.append(source_node)
        created_edges.append(graph.create_edge(
            source_node_id=mission_node["node_id"],
            target_node_id=source_node["node_id"],
            edge_type="cites",
            weight=0.85,
            evidence=[f"Selected source for job {job_id}"],
        ))

    for project in job.get("related_projects", []):
        project_node = graph.upsert_node(
            node_id=f"project:{project.lower().replace(' ', '_')}",
            label=project,
            node_type="project",
            description="ATLAS related project",
            tags=job.get("subject_tags", []),
            properties={},
        )
        created_nodes.append(project_node)
        created_edges.append(graph.create_edge(
            source_node_id=mission_node["node_id"],
            target_node_id=project_node["node_id"],
            edge_type="affects",
            weight=0.75,
            evidence=[f"Project linked in job {job_id}"],
        ))

    job["status"] = "running"
    job["updated_at"] = _utc_now()
    return {"job": job, "nodes": created_nodes, "edges": created_edges}


async def persist_job(job: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.autonomous_knowledge_jobs.update_one({"job_id": job["job_id"]}, {"$set": job}, upsert=True)


async def persist_all_graph(items: Dict[str, Any]) -> None:
    for node in items.get("nodes", []):
        await graph.persist_node(node)
    for edge in items.get("edges", []):
        await graph.persist_edge(edge)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"jobs": 0}
    jobs = await _DB.autonomous_knowledge_jobs.find({}, {"_id": 0}).to_list(5000)
    _ENGINE_JOBS.clear()
    for job in jobs:
        _ENGINE_JOBS[job["job_id"]] = job
    return {"jobs": len(_ENGINE_JOBS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.autonomous_knowledge_jobs.create_index("job_id", unique=True)
    await _DB.autonomous_knowledge_jobs.create_index([("owner_ai", 1), ("status", 1)])
    await _DB.autonomous_knowledge_jobs.create_index("subject_tags")


def reset_in_memory_state() -> None:
    _ENGINE_JOBS.clear()
