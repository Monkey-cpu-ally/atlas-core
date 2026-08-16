from creative_production.project_store import CreativeProjectStore


def test_project_store_preserves_immutable_version_history(tmp_path):
    store = CreativeProjectStore(str(tmp_path / "creative.sqlite3"))
    v1 = store.save_revision(
        project="Night Band",
        payload={"scene": 1, "horn": "ivory", "continuity": ["girl carries horn"]},
        message="initial production snapshot",
    )
    v2 = store.save_revision(
        project="Night Band",
        payload={"scene": 1, "horn": "star-lit ivory", "continuity": ["girl carries horn", "horn glows after sunset"]},
        message="revise horn continuity",
    )

    assert v1.version == 1
    assert v2.version == 2
    assert v2.parent_version == 1
    assert store.get("Night Band", 1).payload["horn"] == "ivory"
    assert store.latest("Night Band").payload["horn"] == "star-lit ivory"
    assert [revision.version for revision in store.history("Night Band")] == [1, 2]
    assert v1.content_hash != v2.content_hash


def test_restore_creates_new_revision_without_destroying_history():
    store = CreativeProjectStore()
    store.save_revision(project="Night Band", payload={"design": "A"}, message="v1")
    store.save_revision(project="Night Band", payload={"design": "B"}, message="v2")
    restored = store.restore(project="Night Band", version=1, message="return to approved design A")

    assert restored.version == 3
    assert restored.parent_version == 2
    assert restored.payload == {"design": "A"}
    assert [r.payload["design"] for r in store.history("Night Band")] == ["A", "B", "A"]
