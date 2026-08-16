from creative_intelligence.reference_library.loader import CreativeReferenceLibrary


def test_default_reference_library_loads_both_catalogs():
    library = CreativeReferenceLibrary.load_default()
    stats = library.stats()
    assert stats["creators"] >= 60
    assert stats["works"] >= 60
    assert stats["total"] == stats["creators"] + stats["works"]


def test_known_creator_and_work_are_queryable():
    library = CreativeReferenceLibrary.load_default()
    assert any(ref.title == "Genndy Tartakovsky" for ref in library.search("Genndy"))
    assert any(ref.title == "Primal" for ref in library.search("Primal"))
    assert any(ref.title == "Rook: Exodus" for ref in library.search("Rook"))


def test_search_can_find_references_by_craft_principle():
    library = CreativeReferenceLibrary.load_default()
    results = library.search("silhouette")
    assert results
    assert any("silhouette" in " ".join(ref.study).lower() for ref in results)


def test_every_reference_has_nonempty_study_principles():
    library = CreativeReferenceLibrary.load_default()
    assert all(ref.study for ref in library.all())
    assert all(all(principle.strip() for principle in ref.study) for ref in library.all())
