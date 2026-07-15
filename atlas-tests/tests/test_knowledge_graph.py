from atlas_knowledge_engine.graph_ingestion import GraphIngestionHook
from atlas_knowledge_engine.graph_models import GraphEdge, GraphNode
from atlas_knowledge_engine.knowledge_graph import KnowledgeGraph
from atlas_knowledge_engine.learning_adapter import ExtractedContent


def test_graph_merges_duplicate_nodes_and_edges():
    graph = KnowledgeGraph()
    first = graph.add_node(GraphNode(node_type="concept", name="Hydrogen", tags=("energy",)))
    second = graph.add_node(GraphNode(node_type="concept", name=" hydrogen ", tags=("fuel",)))

    assert first.node_id == second.node_id
    assert set(second.tags) == {"energy", "fuel"}

    project = graph.add_node(GraphNode(node_type="project", name="Power Cell"))
    edge_a = graph.add_edge(GraphEdge(first.node_id, project.node_id, "supports", weight=0.5))
    edge_b = graph.add_edge(GraphEdge(first.node_id, project.node_id, "SUPPORTS", weight=0.8))

    assert edge_a.edge_id == edge_b.edge_id
    assert edge_b.weight == 0.8
    assert graph.path(first.node_id, project.node_id) == (first.node_id, project.node_id)


def test_graph_ingestion_hook_creates_traceable_relationships():
    graph = KnowledgeGraph()
    hook = GraphIngestionHook(graph)
    content = ExtractedContent(
        source_type="youtube",
        source_id="abc123xyz00",
        title="Hydrogen Storage Explained",
        text="A transcript about hydrogen storage.",
        canonical_url="https://www.youtube.com/watch?v=abc123xyz00",
        creator="Engineering Channel",
        metadata={
            "subjects": ["Physics", "Engineering"],
            "topics": ["Hydrogen", "Cryogenic Storage"],
            "projects": ["Power Cell"],
        },
    )

    hook(content)

    source = graph.find_node("source", "youtube:abc123xyz00")
    creator = graph.find_node("creator", "Engineering Channel")
    hydrogen = graph.find_node("concept", "Hydrogen")
    project = graph.find_node("project", "Power Cell")

    assert source is not None
    assert creator is not None
    assert hydrogen is not None
    assert project is not None
    assert hydrogen in graph.neighbors(source.node_id, relation="discusses")
    assert project in graph.neighbors(source.node_id, relation="supports")
    assert graph.path(creator.node_id, project.node_id) is not None
    assert graph.health()["nodes"] == 7
    assert graph.health()["edges"] == 6
