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
