from services import world_knowledge_graph as wkg


def setup_function():
    wkg.reset_in_memory_state()


def test_seed_foundation_graph_creates_nodes_and_edges():
    result = wkg.seed_foundation_graph()
    summary = wkg.graph_summary()

    assert result["created_nodes"] >= 30
    assert result["created_edges"] >= 30
    assert summary["nodes_by_type"]["country"] >= 10
    assert summary["nodes_by_type"]["source"] >= 10
    assert summary["edges_by_type"]["covers_domain"] >= 10


def test_neighborhood_returns_connected_nodes():
    wkg.seed_foundation_graph()
    hood = wkg.neighborhood("source:nasa", depth=1)

    assert hood["center"]["name"] == "NASA"
    assert hood["node_count"] >= 2
    assert any(node["name"] == "Robotics" for node in hood["nodes"])


def test_create_edge_requires_known_nodes():
    wkg.create_node(node_type="domain", name="Testing", external_id="domain:testing")
    try:
        wkg.create_edge(
            from_node_id="domain:testing",
            to_node_id="missing",
            edge_type="related_to",
        )
    except ValueError as exc:
        assert "unknown to_node_id" in str(exc)
    else:
        raise AssertionError("Expected unknown target node to fail")


def test_node_filtering():
    wkg.seed_foundation_graph()
    sources = wkg.list_nodes(node_type="source", query="JAXA")
    assert len(sources) == 1
    assert sources[0]["name"] == "JAXA"
