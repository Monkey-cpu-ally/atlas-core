"""Bridge the existing Phase-3 research pipeline into the new Knowledge Bank.

This does NOT replace research_pipeline.py. It adds subject-aware planning,
Existing Resource Library lookup, trusted-source priorities, and optional
Knowledge Bank ingestion of already cataloged resources.
"""
from __future__ import annotations

from typing import Any, Dict, List

from services import knowledge_ingestion as ki
from services.existing_resource_library import search_resources
from services.research_pipeline import research_web
from services.subject_source_router import route_subject


async def orchestrate_research(
    *,
    subject: str,
    query: str,
    top_n: int = 5,
    use_live_web: bool = True,
    ingest_catalog_resources: bool = False,
) -> Dict[str, Any]:
    """Run subject-aware research using ATLAS's existing research pipeline.

    Flow:
      subject -> trusted source plan -> existing-resource lookup -> optional
      Knowledge Bank ingestion -> optional live web research.

    Existing catalog entries are never duplicated locally here; ingestion is
    delegated to knowledge_ingestion, which applies URL deduplication and the
    normal distill -> Memory Bank -> graph workflow.
    """
    decision = route_subject(subject)
    if not decision.get("found"):
        raise ValueError(f"unknown ATLAS subject: {subject}")

    canonical = str(decision["subject"])
    preferred_sources: List[str] = list(decision.get("sources") or [])

    # Prefer topic matches, but fall back to subject-wide existing resources.
    catalog = search_resources(subject=canonical, q=query)
    if not catalog:
        catalog = search_resources(subject=canonical)
    catalog = catalog[:top_n]

    ingested: List[Dict[str, Any]] = []
    ingest_errors: List[Dict[str, str]] = []
    if ingest_catalog_resources:
        for resource in catalog:
            url = resource.get("url")
            if not url:
                continue
            try:
                result = await ki.ingest_url(
                    url,
                    extra_tags=[
                        canonical.lower(),
                        "existing-resource",
                        resource.get("resource_type", "resource"),
                    ],
                )
                ingested.append({
                    "resource_id": resource.get("id"),
                    "url": url,
                    "reused": bool(result.get("reused")),
                    "record_id": (result.get("record") or {}).get("id"),
                })
            except Exception as exc:  # noqa: BLE001 - one bad source must not abort research
                ingest_errors.append({
                    "resource_id": str(resource.get("id") or ""),
                    "url": str(url),
                    "error": str(exc),
                })

    live: Dict[str, Any] | None = None
    if use_live_web:
        # Preserve the existing generic web research path, but give it subject
        # context so its results and memories are easier to classify downstream.
        live = await research_web(
            f"{canonical}: {query}",
            top_n=top_n,
            summarise=True,
        )

    return {
        "kind": "orchestrated_research",
        "subject": canonical,
        "query": query,
        "preferred_sources": preferred_sources,
        "persona_affinity": decision.get("persona_affinity", []),
        "all_personas_have_access": decision.get("all_personas_have_access", True),
        "existing_resources": catalog,
        "catalog_ingestion": {
            "requested": ingest_catalog_resources,
            "ingested": ingested,
            "errors": ingest_errors,
        },
        "live_web": live,
    }
