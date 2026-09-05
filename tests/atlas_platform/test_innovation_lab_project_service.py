"""Tests for the ATLAS Innovation Lab project lifecycle service."""

import unittest

from atlas_platform.innovation_lab.project_service import (
    InnovationLabProjectService,
    InvalidProjectTransitionError,
    ProjectNotFoundError,
)
from atlas_platform.schemas.base import LeadAI, ProjectStatus


class InnovationLabProjectServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = InnovationLabProjectService()

    def _create_project(self):
        return self.service.create_project(
            name="Weaver Joint Test Rig",
            category="robotics",
            purpose="Validate one Weaver arm joint before full assembly.",
            lead_ai=LeadAI.HERMES,
            intended_user="ATLAS engineering team",
            operating_environment="bench laboratory",
        )

    def test_create_project_starts_at_intake(self) -> None:
        project = self._create_project()
        self.assertTrue(project.project_id.startswith("project_"))
        self.assertEqual(project.status, ProjectStatus.INTAKE)
        self.assertEqual(project.lead_ai, LeadAI.HERMES)

    def test_valid_lifecycle_transition(self) -> None:
        project = self._create_project()
        updated = self.service.transition_project(project.project_id, ProjectStatus.DISCOVERY)
        self.assertEqual(updated.status, ProjectStatus.DISCOVERY)

    def test_invalid_lifecycle_transition_is_rejected(self) -> None:
        project = self._create_project()
        with self.assertRaises(InvalidProjectTransitionError):
            self.service.transition_project(project.project_id, ProjectStatus.ACTIVE)

    def test_council_decision_is_recorded(self) -> None:
        project = self._create_project()
        updated = self.service.record_council_decision(
            project.project_id,
            "Continue to discovery; validate actuator load assumptions first.",
        )
        self.assertIn("Continue", updated.council_decision)

    def test_unknown_project_raises_specific_error(self) -> None:
        with self.assertRaises(ProjectNotFoundError):
            self.service.get_project("project_missing")

    def test_required_fields_cannot_be_blank(self) -> None:
        with self.assertRaises(ValueError):
            self.service.create_project(
                name=" ",
                category="robotics",
                purpose="test",
                lead_ai=LeadAI.HERMES,
            )


if __name__ == "__main__":
    unittest.main()
