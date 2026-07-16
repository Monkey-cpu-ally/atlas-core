"""Read-only GitHub activity provider for the GENESIS Pulse center.

The route never claims a live connection when credentials are unavailable. It
returns an explicit provider state so the HUD can distinguish live, degraded,
and disconnected data.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/pulse/github", tags=["Pulse"])

GITHUB_API = "https://api.github.com"
DEFAULT_REPOSITORY = os.environ.get("ATLAS_GITHUB_REPOSITORY", "Monkey-cpu-ally/atlas-core")


def _headers() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("ATLAS_GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ATLAS-GENESIS-Pulse",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _pulse_item(
    *,
    item_id: str,
    title: str,
    summary: str,
    occurred_at: str | None,
    url: str | None,
    urgency: str = "normal",
    status: str = "connected",
) -> dict[str, Any]:
    return {
        "id": f"github-{item_id}",
        "sourceId": "github",
        "category": "GitHub",
        "title": title,
        "summary": summary,
        "why": (
            "A failed automated check can block the current ATLAS mission."
            if urgency == "high"
            else "This changes the verified state of an ATLAS project."
        ),
        "persona": "hermes",
        "urgency": urgency,
        "status": status,
        "occurredAt": occurred_at or datetime.now(timezone.utc).isoformat(),
        "url": url,
    }


@router.get("/activity")
async def github_activity(
    repository: str = Query(DEFAULT_REPOSITORY, pattern=r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"),
    limit: int = Query(12, ge=1, le=30),
):
    token_present = bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("ATLAS_GITHUB_TOKEN"))
    items: list[dict[str, Any]] = []

    try:
        async with httpx.AsyncClient(timeout=10.0, headers=_headers()) as client:
            commits_response, runs_response = await client.get(
                f"{GITHUB_API}/repos/{repository}/commits",
                params={"per_page": min(limit, 10)},
            ), await client.get(
                f"{GITHUB_API}/repos/{repository}/actions/runs",
                params={"per_page": min(limit, 10)},
            )

        if commits_response.status_code in {401, 403} or runs_response.status_code in {401, 403}:
            return {
                "provider": "github",
                "repository": repository,
                "connected": False,
                "status": "unauthorized",
                "items": [],
                "message": "GitHub credentials are missing or do not permit this repository.",
            }

        commits_response.raise_for_status()
        runs_response.raise_for_status()

        for commit in commits_response.json()[:limit]:
            detail = commit.get("commit") or {}
            author = detail.get("author") or {}
            message = (detail.get("message") or "Commit created").splitlines()[0]
            items.append(
                _pulse_item(
                    item_id=f"commit-{commit.get('sha', '')[:12]}",
                    title=message,
                    summary=f"Commit added to {repository} by {author.get('name') or 'unknown author'}.",
                    occurred_at=author.get("date"),
                    url=commit.get("html_url"),
                )
            )

        for run in (runs_response.json().get("workflow_runs") or [])[:limit]:
            failed = run.get("conclusion") == "failure"
            state = run.get("conclusion") or run.get("status") or "unknown"
            items.append(
                _pulse_item(
                    item_id=f"workflow-{run.get('id')}",
                    title=f"{run.get('name') or 'Workflow'}: {state}",
                    summary=f"Run #{run.get('run_number')} on {run.get('head_branch') or 'unknown branch'}.",
                    occurred_at=run.get("updated_at") or run.get("created_at"),
                    url=run.get("html_url"),
                    urgency="high" if failed else "normal",
                    status="attention" if failed else "connected",
                )
            )

        items.sort(key=lambda item: item.get("occurredAt") or "", reverse=True)
        return {
            "provider": "github",
            "repository": repository,
            "connected": True,
            "authenticated": token_present,
            "status": "connected",
            "items": items[:limit],
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }
    except httpx.HTTPError as exc:
        return {
            "provider": "github",
            "repository": repository,
            "connected": False,
            "status": "unavailable",
            "items": [],
            "message": f"GitHub is temporarily unavailable: {exc.__class__.__name__}",
        }
