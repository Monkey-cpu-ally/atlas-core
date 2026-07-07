import pytest

from routes import discovery_approval, external_access, project_intelligence
from services import (
    chronicle_engine,
    discovery_approval_pipeline,
    external_access_gateway,
    knowledge_record_writer,
    project_intelligence as project_engine,
)


@pytest.fixture(autouse=True)
def reset_command_surface_state():
    discovery_approval_pipeline.reset_in_memory_state()
    external_access_gateway.reset_in_memory_state()
    project_engine.reset_in_memory_state()
    knowledge_record_writer.reset_in_memory_state()
    chronicle_engine.reset_in_memory_state()


@pytest.mark.asyncio
async def test_discovery_approval_route_promotes_reviewed_discovery_to_knowledge_record():
    draft = await discovery_approval.create_draft(
        discovery_approval.DraftRequest(
            title="Weaver cable routing pattern",
            summary="A verified routing note for keeping Weaver arm cable paths serviceable and inspectable.",
            owner_ai="Hermes",
            evidence=[
                {
                    "source_title": "ATLAS engineering note",
                    "source_type": "internal_test_fixture",
                    "quality": "primary",
                    "relevance": 90,
                    "recency": 80,
                    "notes": "Used to validate the approval route flow.",
                }
            ],
            source_refs=[{"title": "ATLAS engineering note", "kind": "internal_test_fixture"}],
            related_subjects=["Robotics", "Manufacturing"],
            related_projects=["Weaver"],
        )
    )

    review = await discovery_approval.add_review(
        draft["discovery_id"],
        discovery_approval.ReviewRequest(
            reviewer_ai="Council",
            recommendation="approve",
            rationale="Evidence is scoped and safe for an internal ATLAS knowledge record.",
            confidence_score=84,
        ),
    )
    decision = await discovery_approval.council_decision(
        draft["discovery_id"],
        discovery_approval.CouncilDecisionRequest(
            decision="approved",
            rationale="Approved for the Knowledge Bank because evidence, scope, and project links are clear.",
        ),
    )

    assert draft["status"] == "draft"
    assert review["recommendation"] == "approve"
    assert decision["decision"] == "approved"
    assert decision["knowledge_record"]["discovery_id"] == draft["discovery_id"]
    assert decision["chronicle_entry"]["event_type"] == "knowledge_approved"


@pytest.mark.asyncio
async def test_external_access_route_seeds_defaults_and_builds_permission_first_import_plan():
    seeded = await external_access.seed_defaults()
    connections = await external_access.list_connections(owner_ai="Hermes")
    gallery = next(item for item in connections["items"] if item["connector_type"] == "gallery")

    plan = await external_access.create_import_plan(
        gallery["connection_id"],
        external_access.ImportPlanRequest(
            requested_scope="Import selected design references as style tags and color palette notes only.",
            destination_bank="visual_reference_bank",
            related_projects=["ATLAS HUD", "Weaver"],
            require_council_review=True,
        ),
    )

    assert seeded["created_or_updated"] >= 5
    assert gallery["permission_level"] == "read_selected"
    assert gallery["rules"]["store_raw_private_content"] is False
    assert plan["connection_id"] == gallery["connection_id"]
    assert plan["steps"][0] == "Verify permission scope before access."
    assert plan["require_council_review"] is True


@pytest.mark.asyncio
async def test_project_intelligence_route_creates_brief_and_cross_project_reuse_signals():
    weaver = await project_intelligence.create_project(
        project_intelligence.ProjectRequest(
            name="Weaver",
            purpose="Coordinate robotics, manufacturing, and inspection research for ATLAS build systems.",
            owner_ai="Hermes",
            status="active",
            subject_tags=["Robotics", "Manufacturing", "Control Systems"],
        )
    )
    scanner = await project_intelligence.create_project(
        project_intelligence.ProjectRequest(
            name="NIR Scanner",
            purpose="Develop scanning intelligence for materials, blueprints, and digital twin inspection.",
            owner_ai="Hermes",
            status="research",
            subject_tags=["Robotics", "Materials", "Control Systems"],
            related_projects=[weaver["project_id"]],
        )
    )

    await project_intelligence.add_risk(
        weaver["project_id"],
        project_intelligence.RiskRequest(
            title="Cable routing could block maintenance access.",
            severity="medium",
            mitigation="Require service loops, inspection ports, and routing diagrams before prototype approval.",
        ),
    )
    await project_intelligence.add_recommendation(
        weaver["project_id"],
        project_intelligence.RecommendationRequest(
            title="Reuse scanner calibration checks for robotic inspection.",
            owner_ai="Council",
            rationale="The scanner and Weaver share control-system validation needs.",
            confidence_score=78,
        ),
    )

    brief = await project_intelligence.project_brief(weaver["project_id"])
    matches = await project_intelligence.cross_project_matches(scanner["project_id"])

    assert brief["name"] == "Weaver"
    assert brief["counts"]["risks"] == 1
    assert brief["counts"]["recommendations"] == 1
    assert any(match["project_id"] == weaver["project_id"] for match in matches["matches"])
    assert any("Control Systems" in match["shared_tags"] for match in matches["matches"])
