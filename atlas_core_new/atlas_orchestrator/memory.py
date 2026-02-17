"""Project-scoped memory store for Atlas orchestration."""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from threading import RLock
from typing import Any

from .models import AjaniOutput, HermesOutput, MinervaOutput, PipelineStage, ProjectMemorySnapshot, ProjectSummary


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _bump_minor_version(version: str) -> str:
    cleaned = version.strip().lower()
    if not cleaned.startswith("v"):
        return "v0.1"
    try:
        major_str, minor_str = cleaned[1:].split(".")
        major = int(major_str)
        minor = int(minor_str)
    except Exception:
        return "v0.1"
    return f"v{major}.{minor + 1}"


class ProjectMemoryStore:
    def __init__(self, storage_path: Path | None = None) -> None:
        default_path = Path(__file__).resolve().parent.parent / "data" / "atlas_project_memory.json"
        self._storage_path = storage_path or default_path
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def _load_all(self) -> dict[str, Any]:
        if not self._storage_path.exists():
            return {}
        try:
            return json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_all(self, payload: dict[str, Any]) -> None:
        self._storage_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    @staticmethod
    def _default_state(project: str, initial_version: str = "v0.1") -> dict[str, Any]:
        return {
            "project": project,
            "current_version": initial_version,
            "pipeline_stage": "blueprint",
            "last_blueprint": None,
            "parts_list": [],
            "tasks": [],
            "decisions": [],
            "artifacts": {},
            "updated_at": _utc_now(),
        }

    def get_project(
        self,
        project: str,
        *,
        create_if_missing: bool = True,
        initial_version: str = "v0.1",
    ) -> ProjectMemorySnapshot | None:
        with self._lock:
            payload = self._load_all()
            if project not in payload:
                if not create_if_missing:
                    return None
                payload[project] = self._default_state(project, initial_version=initial_version)
                self._save_all(payload)
            return ProjectMemorySnapshot(**payload[project])

    def list_projects(self) -> list[ProjectSummary]:
        with self._lock:
            payload = self._load_all()
            summaries: list[ProjectSummary] = []
            for state in payload.values():
                summaries.append(
                    ProjectSummary(
                        project=state["project"],
                        current_version=state["current_version"],
                        pipeline_stage=state["pipeline_stage"],
                        updated_at=state["updated_at"],
                    )
                )
            summaries.sort(key=lambda item: item.updated_at, reverse=True)
            return summaries

    def reset_project(self, project: str, *, initial_version: str = "v0.1") -> ProjectMemorySnapshot:
        with self._lock:
            payload = self._load_all()
            payload[project] = self._default_state(project, initial_version=initial_version)
            self._save_all(payload)
            return ProjectMemorySnapshot(**payload[project])

    def update_after_run(
        self,
        *,
        project: str,
        stage: PipelineStage,
        ajani: AjaniOutput,
        minerva: MinervaOutput,
        hermes: HermesOutput,
        intent: str,
        user_input: str,
    ) -> ProjectMemorySnapshot:
        with self._lock:
            payload = self._load_all()
            state = payload.get(project, self._default_state(project))

            if stage == "modify":
                state["current_version"] = _bump_minor_version(state.get("current_version", "v0.1"))

            state["pipeline_stage"] = stage
            if stage == "blueprint":
                state["last_blueprint"] = {
                    "summary": ajani.summary,
                    "structured_plan": ajani.structured_plan,
                    "component_breakdown": ajani.component_breakdown,
                    "measurable_requirements": ajani.measurable_requirements,
                }

            state["parts_list"] = _dedupe_keep_order(
                [*state.get("parts_list", []), *ajani.parts_list]
            )[:200]
            state["tasks"] = _dedupe_keep_order(
                [*state.get("tasks", []), *minerva.lego_steps]
            )[:300]
            state["decisions"] = (
                [*state.get("decisions", []), f"{hermes.validation_status.upper()}: {hermes.summary}"]
            )[-150:]
            state["artifacts"] = {
                **state.get("artifacts", {}),
                "last_intent": intent,
                "last_user_input": user_input[:400],
                "last_validation_status": hermes.validation_status,
            }
            state["updated_at"] = _utc_now()
            state["project"] = project

            payload[project] = state
            self._save_all(payload)
            return ProjectMemorySnapshot(**state)

