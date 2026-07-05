"""ATLAS Source Code Connector.

Safe metadata-only connector for approved open-source repositories. This lets
ATLAS inspect repository-level signals, recent commits, and file tree metadata
without cloning or storing full source code.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlparse

import httpx

from services import world_knowledge_connector as registry

DEFAULT_TIMEOUT = 12.0
USER_AGENT = "ATLAS-SourceCodeConnector/1.0 (+metadata-only)"


class SourceCodeConnectorError(RuntimeError):
    """Raised when a source-code preview cannot complete safely."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_github_repo(url: str) -> Dict[str, str]:
    """Parse a GitHub repository URL into owner/repo."""
    parsed = urlparse(url)
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        raise SourceCodeConnectorError("only github.com repository URLs are supported in v1")
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        raise SourceCodeConnectorError("GitHub URL must include owner and repository name")
    return {"owner": parts[0], "repo": parts[1].replace(".git", "")}


def _headers() -> Dict[str, str]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def _github_get(path: str) -> Any:
    url = f"https://api.github.com{path}"
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, follow_redirects=True, headers=_headers()) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def preview_github_repository(source_id: str, commit_limit: int = 5, tree_limit: int = 30) -> Dict[str, Any]:
    """Return safe repository metadata for an approved source-code registry item."""
    source = registry.get_source(source_id)
    if not source:
        raise SourceCodeConnectorError(f"unknown source_id: {source_id}")
    source_type = str(source.get("source_type", ""))
    planned = registry.plan_sync_job(source_id)
    if planned.get("connector_type") != "github" and "repository" not in source_type:
        raise SourceCodeConnectorError(f"source is not registered as a source-code repository: {source_id}")

    repo_info = parse_github_repo(source.get("url", ""))
    owner = repo_info["owner"]
    repo = repo_info["repo"]

    repo_meta = await _github_get(f"/repos/{owner}/{repo}")
    commits_raw = await _github_get(f"/repos/{owner}/{repo}/commits?per_page={max(1, min(commit_limit, 10))}")
    contents_raw = await _github_get(f"/repos/{owner}/{repo}/contents")

    commits: List[Dict[str, Any]] = []
    for item in commits_raw[: max(1, min(commit_limit, 10))]:
        commit = item.get("commit", {})
        commits.append({
            "sha": item.get("sha", "")[:12],
            "message": (commit.get("message") or "").split("\n")[0][:240],
            "author": (commit.get("author") or {}).get("name"),
            "date": (commit.get("author") or {}).get("date"),
            "url": item.get("html_url"),
        })

    top_level_files: List[Dict[str, Any]] = []
    for item in contents_raw[: max(1, min(tree_limit, 100))]:
        top_level_files.append({
            "name": item.get("name"),
            "path": item.get("path"),
            "type": item.get("type"),
            "size": item.get("size"),
        })

    return {
        "source_id": source_id,
        "source_name": source.get("name"),
        "ai_owner": source.get("ai_owner"),
        "connector_type": "github",
        "fetched_at": _utc_now(),
        "url": source.get("url"),
        "repo": f"{owner}/{repo}",
        "description": repo_meta.get("description"),
        "default_branch": repo_meta.get("default_branch"),
        "language": repo_meta.get("language"),
        "stars": repo_meta.get("stargazers_count"),
        "forks": repo_meta.get("forks_count"),
        "open_issues": repo_meta.get("open_issues_count"),
        "license": (repo_meta.get("license") or {}).get("spdx_id"),
        "pushed_at": repo_meta.get("pushed_at"),
        "recent_commits": commits,
        "top_level_files": top_level_files,
        "content_stored": False,
        "copyright_rule": "repository metadata, commit messages, and file tree only; no full source files stored",
    }
