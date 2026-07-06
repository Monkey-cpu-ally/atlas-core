import pytest

from routes import headquarters


@pytest.mark.asyncio
async def test_status_route_returns_headquarters_snapshot():
    response = await headquarters.status()

    assert response["name"] == "ATLAS Headquarters"
    assert response["active_operation"] == "Operation ATLAS Refinement"
    assert response["release_posture"] == "not_ready_until_verified"
    assert response["divisions"]


@pytest.mark.asyncio
async def test_quality_gates_route_returns_required_gates():
    response = await headquarters.quality_gates()
    gate_names = {gate["gate"] for gate in response["gates"]}

    assert response["title"] == "ATLAS Quality Gate Report"
    assert response["approval_status"] == "pending"
    assert {"Built", "Connected", "Tested", "Cleaned", "Documented", "Approved"}.issubset(gate_names)


@pytest.mark.asyncio
async def test_atlas_standard_route_maps_generic_routes():
    response = await headquarters.atlas_standard()
    replacement_map = response["generic_replacement_map"]

    assert response["title"] == "ATLAS Luxury Engineering Standard"
    assert replacement_map["/api/discovery-approval"] == "/api/headquarters/knowledge-gate"
    assert replacement_map["/api/external-access"] == "/api/headquarters/source-clearance"
    assert replacement_map["/api/project-intelligence"] == "/api/headquarters/project-briefing"


@pytest.mark.asyncio
async def test_mission_control_route_blocks_until_phase_verified():
    response = await headquarters.mission_control()

    assert response["title"] == "ATLAS Mission Control"
    assert response["active"]["operation"] == "Operation ATLAS Refinement"
    assert response["blocked_until"] == "Phase 14 verification passes."


@pytest.mark.asyncio
async def test_knowledge_gate_route_presents_discovery_approval_as_atlas_surface():
    response = await headquarters.knowledge_gate()

    assert response["title"] == "ATLAS Knowledge Gate"
    assert response["identity"] == "ATLAS Headquarters Command Surface"
    assert response["developer_api_underneath"] == "/api/discovery-approval"
    assert response["owner"] == "Minerva + Council"


@pytest.mark.asyncio
async def test_source_clearance_route_presents_external_access_as_atlas_surface():
    response = await headquarters.source_clearance()

    assert response["title"] == "ATLAS Source Clearance"
    assert response["developer_api_underneath"] == "/api/external-access"
    assert response["owner"] == "Council"


@pytest.mark.asyncio
async def test_project_briefing_route_presents_project_intelligence_as_atlas_surface():
    response = await headquarters.project_briefing()

    assert response["title"] == "ATLAS Project Briefing"
    assert response["developer_api_underneath"] == "/api/project-intelligence"
    assert response["current_state"] == "active_foundation_needs_more_tests"


@pytest.mark.asyncio
async def test_refinement_route_presents_self_improve_as_atlas_surface():
    response = await headquarters.refinement()

    assert response["title"] == "ATLAS Refinement Office"
    assert response["developer_api_underneath"] == "/api/self-improve"
    assert response["quality_gate"] == "pending_headquarters_approval"
