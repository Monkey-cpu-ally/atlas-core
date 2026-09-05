"""Persistence and scoring tests for the ATLAS Innovation Lab."""

import tempfile
import unittest
from pathlib import Path

from atlas_platform.innovation_lab.scoring import CRITERIA, score_innovation
from atlas_platform.innovation_lab.sqlite_repository import SQLiteProjectRepository
from atlas_platform.schemas.base import AtlasProject, LeadAI, ProjectStatus


class SQLiteProjectRepositoryTests(unittest.TestCase):
    def test_project_survives_repository_restart(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "innovation_lab.db"
            project = AtlasProject(
                project_id="project_persistence_test",
                name="Digital Twin Test",
                category="simulation",
                purpose="Prove persistent Innovation Lab state.",
                lead_ai=LeadAI.HERMES,
                status=ProjectStatus.DIGITAL_TWIN,
                tags=["test", "digital-twin"],
                metadata={"revision": 1},
            )
            SQLiteProjectRepository(database).save(project)

            restarted_repository = SQLiteProjectRepository(database)
            restored = restarted_repository.get(project.project_id)

            self.assertIsNotNone(restored)
            self.assertEqual(restored, project)

    def test_status_filter_returns_matching_projects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = SQLiteProjectRepository(Path(directory) / "lab.db")
            repository.save(
                AtlasProject(
                    project_id="project_one",
                    name="One",
                    category="robotics",
                    purpose="test",
                    lead_ai=LeadAI.HERMES,
                )
            )
            repository.save(
                AtlasProject(
                    project_id="project_two",
                    name="Two",
                    category="science",
                    purpose="test",
                    lead_ai=LeadAI.MINERVA,
                    status=ProjectStatus.PAUSED,
                )
            )
            results = repository.list(status=ProjectStatus.PAUSED)
            self.assertEqual([project.project_id for project in results], ["project_two"])


class InnovationScoringTests(unittest.TestCase):
    def test_complete_high_score_advances(self) -> None:
        result = score_innovation({criterion: 9 for criterion in CRITERIA})
        self.assertEqual(result.percentage, 90.0)
        self.assertEqual(result.recommendation, "advance")

    def test_partial_rubric_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            score_innovation({"novelty": 8})

    def test_out_of_range_score_is_rejected(self) -> None:
        scores = {criterion: 8 for criterion in CRITERIA}
        scores["safety"] = 11
        with self.assertRaises(ValueError):
            score_innovation(scores)


if __name__ == "__main__":
    unittest.main()
