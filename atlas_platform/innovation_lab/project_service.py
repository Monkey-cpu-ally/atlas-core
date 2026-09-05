"""Project lifecycle service for the ATLAS Innovation Lab."""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, Iterable, Optional

from atlas_platform.core.ids import new_id
from atlas_platform.schemas.base import AtlasProject, LeadAI, ProjectStatus


class ProjectNotFoundError(KeyError):
    """Raised when an Innovation Lab project cannot be found."""


class InvalidProjectTransitionError(ValueError):
    """Raised when a project attempts an illegal lifecycle transition."""


_ALLOWED_TRANSITIONS = {
    ProjectStatus.INTAKE: {ProjectStatus.DISCOVERY, ProjectStatus.PAUSED, ProjectStatus.ARCHIVED},
    ProjectStatus.DISCOVERY: {ProjectStatus.CONCEPT, ProjectStatus.PAUSED, ProjectStatus.ARCHIVED},
    ProjectStatus.CONCEPT: {ProjectStatus.DIGITAL_TWIN, ProjectStatus.PROTOTYPE, ProjectStatus.PAUSED, ProjectStatus.ARCHIVED},
    ProjectStatus.DIGITAL_TWIN: {ProjectStatus.PROTOTYPE, ProjectStatus.CONCEPT, ProjectStatus.PAUSED, ProjectStatus.ARCHIVED},
    ProjectStatus.PROTOTYPE: {ProjectStatus.ACTIVE, ProjectStatus.DIGITAL_TWIN, ProjectStatus.PAUSED, ProjectStatus.ARCHIVED},
    ProjectStatus.ACTIVE: {ProjectStatus.PROTOTYPE, ProjectStatus.PAUSED, ProjectStatus.ARCHIVED},
    ProjectStatus.PAUSED: {
        ProjectStatus.DISCOVERY,
        ProjectStatus.CONCEPT,
        ProjectStatus.DIGITAL_TWIN,
        ProjectStatus.PROTOTYPE,
        ProjectStatus.ACTIVE,
        ProjectStatus.ARCHIVED,
    },
    ProjectStatus.ARCHIVED: set(),
}


class InnovationLabProjectService:
    """Create and manage Innovation Lab projects.

    This first implementation intentionally uses an in-memory repository so the
    lifecycle rules can be tested independently of SQLite or another database.
    Persistent storage can later implement the same service contract.
    """

    def __init__(self) -> None:
        self._projects: Dict[str, AtlasProject] = {}

    def create_project(
        self,
        *,
        name: str,
        category: str,
        purpose: str,
        lead_ai: LeadAI,
        intended_user: Optional[str] = None,
        operating_environment: Optional[str] = None,
    ) -> AtlasProject:
        name = name.strip()
        category = category.strip()
        purpose = purpose.strip()
        if not name:
            raise ValueError("project name is required")
        if not category:
            raise ValueError("project category is required")
        if not purpose:
            raise ValueError("project purpose is required")

        project = AtlasProject(
            project_id=new_id("project"),
            name=name,
            category=category,
            purpose=purpose,
            lead_ai=lead_ai,
            intended_user=intended_user,
            operating_environment=operating_environment,
        )
        self._projects[project.project_id] = project
        return project

    def get_project(self, project_id: str) -> AtlasProject:
        try:
            return self._projects[project_id]
        except KeyError as exc:
            raise ProjectNotFoundError(project_id) from exc

    def list_projects(self, *, status: Optional[ProjectStatus] = None) -> Iterable[AtlasProject]:
        projects = self._projects.values()
        if status is None:
            return tuple(projects)
        return tuple(project for project in projects if project.status is status)

    def transition_project(self, project_id: str, target: ProjectStatus) -> AtlasProject:
        project = self.get_project(project_id)
        if target is project.status:
            return project

        allowed = _ALLOWED_TRANSITIONS[project.status]
        if target not in allowed:
            raise InvalidProjectTransitionError(
                f"cannot move project from {project.status.value} to {target.value}"
            )

        updated = replace(project, status=target)
        self._projects[project_id] = updated
        return updated

    def record_council_decision(self, project_id: str, decision: str) -> AtlasProject:
        decision = decision.strip()
        if not decision:
            raise ValueError("council decision is required")
        project = self.get_project(project_id)
        updated = replace(project, council_decision=decision)
        self._projects[project_id] = updated
        return updated
