import json
from pathlib import Path

import pytest

from creative_intelligence.reference_library.loader import CreativeReferenceLibrary

LIBRARY_DIR = Path(__file__).parents[1] / "creative_intelligence" / "reference_library"


def test_default_library_loads_seed_catalogs():
    library = CreativeReferenceLibrary.load_default()
    stats = library.stats()
    assert stats["creators"] >= 24
    assert stats["works"] >= 35
    assert stats["total"] == stats["creators"] + stats["works"]


def test_reference_ids_are_unique_and_retrievable():
    library = CreativeReferenceLibrary.load_default()
    ids = [reference.reference_id for reference in library.all()]
    assert len(ids) == len(set(ids))
    for reference in library.all():
        assert library.get(reference.reference_id) == reference


def test_search_matches_title_category_and_craft_principles():
    library = CreativeReferenceLibrary.load_default()
    assert any(ref.title == "Genndy Tartakovsky" for ref in library.search("minimal dialogue"))
    assert any(ref.title == "Bloodborne" for ref in library.search("cosmic-horror"))
    assert any(ref.kind == "creator" for ref in library.search("literature"))


def test_ranked_retrieval_exposes_score_and_matching_terms():
    library = CreativeReferenceLibrary.load_default()
    matches = library.retrieve("minimal dialogue visual storytelling", limit=5)
    assert matches
    assert all(match.score > 0 for match in matches)
    assert all(match.matched_terms for match in matches)
    assert list(matches) == sorted(matches, key=lambda m: (-m.score, m.reference.title.casefold(), m.reference.reference_id))


def test_ranked_retrieval_can_filter_creator_and_work():
    library = CreativeReferenceLibrary.load_default()
    creators = library.retrieve("horror", kind="creator")
    works = library.retrieve("horror", kind="work")
    assert creators and all(match.reference.kind == "creator" for match in creators)
    assert works and all(match.reference.kind == "work" for match in works)


def test_ranked_retrieval_fails_closed_on_invalid_contract():
    library = CreativeReferenceLibrary.load_default()
    with pytest.raises(ValueError, match="positive"):
        library.retrieve("horror", limit=0)
    with pytest.raises(ValueError, match="creator or work"):
        library.retrieve("horror", kind="unknown")


def test_catalogs_declare_originality_and_provenance_rules():
    creators = json.loads((LIBRARY_DIR / "creative_masters.json").read_text(encoding="utf-8"))
    works = json.loads((LIBRARY_DIR / "works_catalog.json").read_text(encoding="utf-8"))
    rules = " ".join(creators.get("rules", [])).lower()
    purpose = f"{creators.get('purpose', '')} {works.get('purpose', '')}".lower()
    assert "provenance" in rules
    assert "reject direct imitation" in rules
    assert "never" in purpose and ("clone" in purpose or "reproduce" in purpose)


def test_loader_fails_closed_on_duplicate_reference_ids():
    library = CreativeReferenceLibrary.load_default()
    first = library.all()[0]
    with pytest.raises(ValueError, match="duplicate creative reference id"):
        CreativeReferenceLibrary([first, first])
