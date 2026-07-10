import pytest
from fastapi import HTTPException

from routes import world_knowledge_graph
from services import world_knowledge_graph as wkg


@pytest.fixture(autouse=True)
def reset_world_graph_state():
    wkg.attach_mongo(None)
    wkg.reset_in_memory_state()


@pytest.mark.asyncio
async def test_health_route_reports_world_graph_engine_state():
    response = await world_knowledge_graph.health()

    assert response == {
        "status": "ok",
        "engine": "world_knowledge_graph",
        "persistence_enabled": False,
        "node_count": 0,
    }


@pytest.mark.asyncio
async def test_seed_and_summary_routes_build_foundation_graph():
    seeded = await world_knowledge_graph.seed_foundation_graph()
    summary = await world_knowledge_graph.summary()

    assert seeded["created_nodes"] > 0
    assert seeded["created_edges"] > 0
    assert summary["title"] == "ATLAS World Knowledge Graph Summary"
    assert summary["node_count"] == seeded["created_nodes"]
    assert summary["edge_count"] == seeded["created_edges"]
    assert summary["nodes_by_type"]["project"] >= 3
    assert summary["nodes_by_type"]["source"] >= 1


@pytest.mark.asyncio
async def test_node_routes_create_filter_and_fetch_nodes():
    node = await world_knowledge_graph.create_node(
        world_knowledge_graph.NodeRequest(
            node_type="technology",
            name="ATLAS Test Technology",
            owner_ai="Hermes",
            external_id="technology:atlas-test",
            metadata={"readiness": "research"},
        )
    )

    listed = await world_knowledge_graph.list_nodes(
        node_type="technology",
        owner_ai="Hermes",
        query="atlas test",
        limit=25,
    )
    fetched = await world_knowledge_graph.get_node(node["node_id"])

    assert node["node_id"] == "technology:atlas-test"
    assert listed["count"] == 1
    assert listed["items"][0]["metadata"]["readiness"] == "research"
    assert fetched == node


@pytest.mark.asyncio
async def test_edge_and_neighborhood_routes_connect_nodes():
    project = await world_knowledge_graph.create_node(
        world_knowledge_graph.NodeRequest(
            node_type="project",
            name="ATLAS Persistence Lab",
            external_id="project:persistence-lab",
        )
    )
    domain = await world_knowledge_graph.create_node(
        world_knowledge_graph.NodeRequest(
            node_type="domain",
            name="Software Engineering",
            owner_ai="Minerva",
            external_id="domain:software-engineering-test",
        )
    )
    edge = await world_knowledge_graph.create_edge(
        world_knowledge_graph.EdgeRequest(
            from_node_id=project["node_id"],
            to_node_id=domain["node_id"],
            edge_type="covers_domain",
            confidence_score=93,
            rationale="The project validates ATLAS software persistence behavior.",
        )
    )

    edges = await world_knowledge_graph.list_edges(
        node_id=project["node_id"],
        edge_type="covers_domain",
        limit=20,
    )
    neighborhood = await world_knowledge_graph.neighborhood(
        node_id=project["node_id"],
        depth=1,
        limit=20,
    )

    assert edges["count"] == 1
    assert edges["items"][0]["edge_id"] == edge["edge_id"]
    assert neighborhood["center"]["node_id"] == project["node_id"]
    assert neighborhood["node_count"] == 2
    assert neighborhood["edge_count"] == 1
    assert {item["node_id"] for item in neighborhood["nodes"]} == {
        project["node_id"],
        domain["node_id"],
    }


@pytest.mark.asyncio
async def test_routes_translate_invalid_graph_operations_to_http_errors():
    with pytest.raises(HTTPException) as invalid_node:
        await world_knowledge_graph.create_node(
            world_knowledge_graph.NodeRequest(
                node_type="unknown",
                name="Invalid Graph Node",
            )
        )
    assert invalid_node.value.status_code == 422

    with pytest.raises(HTTPException) as missing_node:
        await world_knowledge_graph.get_node("missing:node")
    assert missing_node.value.status_code == 404

    with pytest.raises(HTTPException) as invalid_edge:
        await world_knowledge_graph.create_edge(
            world_knowledge_graph.EdgeRequest(
                from_node_id="missing:from",
                to_node_id="missing:to",
                edge_type="related_to",
            )
        )
    assert invalid_edge.value.status_code == 422

    with pytest.raises(HTTPException) as missing_neighborhood:
        await world_knowledge_graph.neighborhood("missing:center")
    assert missing_neighborhood.value.status_code == 404
