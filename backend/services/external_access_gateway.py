"""ATLAS External Access Gateway.

Permission-first registry for external sources such as Ivy Tech, YouTube,
Gallery, Google Drive, Figma, CAD, and future tools. This gateway does not pull
private data by itself; it records what ATLAS is allowed to access, which AI owns
that connection, and how imported knowledge should be handled.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

VALID_CONNECTOR_TYPES = {
    "ivytech", "youtube", "gallery", "google_drive", "figma", "cad",
    "calendar", "gmail", "github", "local_files", "simulation", "custom",
}
VALID_AI_OWNERS = {"Ajani", "Hermes", "Minerva", "Council"}
VALID_PERMISSION_LEVELS = {"none", "metadata_only", "read_selected", "read_approved", "write_drafts"}
VALID_STATUSES = {"planned", "connected", "paused", "revoked", "error"}

_CONNECTIONS: Dict[str, Dict[str, Any]] = {}
_IMPORT_PLANS: Dict[str, Dict[str, Any]] = {}
_DB: Any = None


class ExternalAccessError(RuntimeError):
    """Raised when an external access operation is invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_connection(
    *,
    name: str,
    connector_type: str,
    purpose: str,
    owner_ai: str,
    allowed_content: Optional[List[str]] = None,
    blocked_content: Optional[List[str]] = None,
    permission_level: str = "metadata_only",
    status: str = "planned",
    connection_config: Optional[Dict[str, Any]] = None,
    connection_id: Optional[str] = None,
) -> Dict[str, Any]:
    if connector_type not in VALID_CONNECTOR_TYPES:
        raise ExternalAccessError(f"invalid connector_type: {connector_type}")
    if owner_ai not in VALID_AI_OWNERS:
        raise ExternalAccessError(f"invalid owner_ai: {owner_ai}")
    if permission_level not in VALID_PERMISSION_LEVELS:
        raise ExternalAccessError(f"invalid permission_level: {permission_level}")
    if status not in VALID_STATUSES:
        raise ExternalAccessError(f"invalid status: {status}")

    cid = connection_id or f"external:{connector_type}:{_slug(name)}"
    record = {
        "connection_id": cid,
        "name": name,
        "connector_type": connector_type,
        "purpose": purpose,
        "owner_ai": owner_ai,
        "allowed_content": allowed_content or [],
        "blocked_content": blocked_content or [],
        "permission_level": permission_level,
        "status": status,
        "connection_config": connection_config or {},
        "last_checked_at": None,
        "last_import_plan_id": None,
        "rules": {
            "store_raw_private_content": False,
            "summarize_in_own_words": True,
            "cite_origin": True,
            "require_user_approval_for_new_scope": True,
        },
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _CONNECTIONS[cid] = record
    return record


def upsert_connection(**kwargs: Any) -> Dict[str, Any]:
    connection_id = kwargs.get("connection_id") or f"external:{kwargs.get('connector_type')}:{_slug(kwargs.get('name', 'unnamed'))}"
    if connection_id in _CONNECTIONS:
        record = _CONNECTIONS[connection_id]
        for key in (
            "name", "connector_type", "purpose", "owner_ai", "allowed_content",
            "blocked_content", "permission_level", "status", "connection_config",
        ):
            if key in kwargs and kwargs[key] is not None:
                record[key] = kwargs[key]
        record["updated_at"] = _utc_now()
        return record
    kwargs["connection_id"] = connection_id
    return create_connection(**kwargs)


def get_connection(connection_id: str) -> Optional[Dict[str, Any]]:
    return _CONNECTIONS.get(connection_id)


def list_connections(
    connector_type: Optional[str] = None,
    owner_ai: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    items = list(_CONNECTIONS.values())
    if connector_type:
        items = [item for item in items if item["connector_type"] == connector_type]
    if owner_ai:
        items = [item for item in items if item["owner_ai"].lower() == owner_ai.lower()]
    if status:
        items = [item for item in items if item["status"] == status]
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)


def create_import_plan(
    *,
    connection_id: str,
    requested_scope: str,
    destination_bank: str = "knowledge_bank",
    related_projects: Optional[List[str]] = None,
    require_council_review: bool = True,
) -> Dict[str, Any]:
    connection = get_connection(connection_id)
    if not connection:
        raise ExternalAccessError(f"unknown connection_id: {connection_id}")
    if connection["status"] not in {"planned", "connected"}:
        raise ExternalAccessError(f"connection is not importable: {connection['status']}")
    if connection["permission_level"] == "none":
        raise ExternalAccessError("connection permission level is none")

    plan_id = f"IMPORT-{str(uuid4())[:8]}"
    plan = {
        "import_plan_id": plan_id,
        "connection_id": connection_id,
        "connection_name": connection["name"],
        "connector_type": connection["connector_type"],
        "owner_ai": connection["owner_ai"],
        "requested_scope": requested_scope,
        "permission_level": connection["permission_level"],
        "destination_bank": destination_bank,
        "related_projects": related_projects or [],
        "require_council_review": require_council_review,
        "status": "planned",
        "steps": [
            "Verify permission scope before access.",
            "Pull only allowed metadata or selected content.",
            "Summarize in ATLAS's own words.",
            "Attach citation/origin metadata.",
            "Submit discovery for Council review if required.",
        ],
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _IMPORT_PLANS[plan_id] = plan
    connection["last_import_plan_id"] = plan_id
    connection["updated_at"] = _utc_now()
    return plan


def list_import_plans(connection_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    items = list(_IMPORT_PLANS.values())
    if connection_id:
        items = [item for item in items if item["connection_id"] == connection_id]
    if status:
        items = [item for item in items if item["status"] == status]
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)


def seed_default_connections() -> Dict[str, Any]:
    defaults = [
        {
            "name": "Ivy Tech Coursework",
            "connector_type": "ivytech",
            "purpose": "Organize coursework, assignments, notes, study plans, and software development learning.",
            "owner_ai": "Minerva",
            "allowed_content": ["course titles", "assignment metadata", "user-selected notes", "study materials"],
            "blocked_content": ["passwords", "student financial data", "private messages unless selected"],
            "permission_level": "metadata_only",
        },
        {
            "name": "YouTube Learning Sources",
            "connector_type": "youtube",
            "purpose": "Extract concepts from approved videos and channels for ATLAS learning and projects.",
            "owner_ai": "Council",
            "allowed_content": ["public video metadata", "transcripts when available", "user-approved channels"],
            "blocked_content": ["copyrighted full-video storage"],
            "permission_level": "read_approved",
        },
        {
            "name": "Gallery Visual Reference Library",
            "connector_type": "gallery",
            "purpose": "Let Hermes learn visual style patterns from user-approved images without copying them.",
            "owner_ai": "Hermes",
            "allowed_content": ["user-selected images", "style tags", "color palettes", "design notes"],
            "blocked_content": ["faces/identity analysis", "private family images unless explicitly selected", "raw image redistribution"],
            "permission_level": "read_selected",
        },
        {
            "name": "Figma HUD Design Files",
            "connector_type": "figma",
            "purpose": "Connect ATLAS HUD concepts, design components, and visual systems to frontend implementation.",
            "owner_ai": "Hermes",
            "allowed_content": ["selected design files", "components", "tokens", "layout references"],
            "blocked_content": ["unapproved team files"],
            "permission_level": "read_selected",
        },
        {
            "name": "Google Drive Research Vault",
            "connector_type": "google_drive",
            "purpose": "Organize selected PDFs, docs, blueprints, and research notes into ATLAS banks.",
            "owner_ai": "Council",
            "allowed_content": ["user-selected files", "PDF metadata", "document summaries"],
            "blocked_content": ["unselected personal files", "credentials", "financial data"],
            "permission_level": "read_selected",
        },
        {
            "name": "CAD Blueprint Workspace",
            "connector_type": "cad",
            "purpose": "Prepare selected CAD models and blueprint metadata for Hermes and Ajani review.",
            "owner_ai": "Hermes",
            "allowed_content": ["selected CAD files", "model metadata", "dimensions", "assembly notes"],
            "blocked_content": ["unapproved proprietary files"],
            "permission_level": "read_selected",
        },
    ]
    created = []
    for item in defaults:
        created.append(upsert_connection(**item))
    return {"created_or_updated": len(created), "items": created}


async def persist_connection(record: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.external_access_connections.update_one({"connection_id": record["connection_id"]}, {"$set": record}, upsert=True)


async def persist_import_plan(plan: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.external_access_import_plans.update_one({"import_plan_id": plan["import_plan_id"]}, {"$set": plan}, upsert=True)


async def persist_all(items: List[Dict[str, Any]]) -> None:
    for item in items:
        await persist_connection(item)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"connections": 0, "import_plans": 0}
    conns = await _DB.external_access_connections.find({}, {"_id": 0}).to_list(5000)
    plans = await _DB.external_access_import_plans.find({}, {"_id": 0}).to_list(5000)
    _CONNECTIONS.clear()
    _IMPORT_PLANS.clear()
    for conn in conns:
        _CONNECTIONS[conn["connection_id"]] = conn
    for plan in plans:
        _IMPORT_PLANS[plan["import_plan_id"]] = plan
    return {"connections": len(_CONNECTIONS), "import_plans": len(_IMPORT_PLANS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.external_access_connections.create_index("connection_id", unique=True)
    await _DB.external_access_connections.create_index([("connector_type", 1), ("owner_ai", 1)])
    await _DB.external_access_import_plans.create_index("import_plan_id", unique=True)
    await _DB.external_access_import_plans.create_index([("connection_id", 1), ("status", 1)])


def reset_in_memory_state() -> None:
    _CONNECTIONS.clear()
    _IMPORT_PLANS.clear()
