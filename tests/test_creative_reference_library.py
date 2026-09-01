import json
from pathlib import Path

import pytest

from creative_intelligence.reference_library.loader import CreativeReference, CreativeReferenceLibrary

LIBRARY_DIR = Path(__file__).parents[1] / "creative_intelligence" / "reference_library"


def test_default_library_loads_seed_catalogs():
    library = CreativeReferenceLibrary.load_default()
    stats = library.stats()
    assert stats["creators"] >= 53
    assert stats["works"] >= 35
    assert stats["total"] == stats["creators"] + stats["works"]
    assert stats["profiled"] >= 21


def test_reference_ids_are_unique_and_retrievable():
    library = CreativeReferenceLibrary.load_default()
    ids = [reference.reference_id for reference in library.all()]
    assert len(ids) == len(set(ids))
    for reference in library.all():
        assert library.get(reference.reference_id) == reference


def test_profile_schema_is_backward_compatible():
    reference = CreativeReference("creator:test", "Test", "creator", "art", ("composition",))
    assert reference.disciplines == ()
    assert reference.techniques == ()
    assert reference.strengths == ()
    assert reference.study_targets == ()
    assert reference.limitations == ()
    assert reference.provenance == ()
    assert reference.relationships == ()


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


def test_ranked_retrieval_uses_deep_profile_fields():
    reference = CreativeReference(
        "creator:test",
        "Test Creator",
        "creator",
        "design",
        ("composition",),
        disciplines=("industrial design",),
        techniques=("functional silhouette",),
        strengths=("readability",),
        study_targets=("vehicle architecture",),
        limitations=("do not imitate signature forms",),
        provenance=("curated editorial profile",),
        relationships=("environment design",),
    )
    library = CreativeReferenceLibrary([reference])
    match = library.retrieve("vehicle architecture")[0]
    assert match.reference == reference
    assert {"vehicle", "architecture"}.issubset(set(match.matched_terms))
    assert library.search("functional silhouette") == (reference,)


def test_synthesis_combines_multiple_references_and_preserves_boundaries():
    library = CreativeReferenceLibrary.load_default()
    synthesis = library.synthesize("minimal dialogue visual storytelling", limit=4)
    assert len(synthesis.references) >= 2
    assert synthesis.principles
    assert synthesis.study_targets
    assert synthesis.limitations
    assert synthesis.provenance
    assert len(synthesis.principles) == len({value.casefold() for value in synthesis.principles})
    assert any("do not" in value.casefold() for value in synthesis.limitations)


def test_synthesis_is_deterministic_for_same_query():
    library = CreativeReferenceLibrary.load_default()
    first = library.synthesize("industrial science fiction design", limit=4)
    second = library.synthesize("industrial science fiction design", limit=4)
    assert first == second


def test_synthesis_fails_closed_without_reference_diversity():
    reference = CreativeReference("creator:one", "One", "creator", "design", ("shape",))
    library = CreativeReferenceLibrary([reference])
    with pytest.raises(ValueError, match="insufficient references"):
        library.synthesize("shape")
    with pytest.raises(ValueError, match="at least two references"):
        library.synthesize("shape", minimum_references=1)
    with pytest.raises(ValueError, match="limit must meet minimum"):
        library.synthesize("shape", limit=2, minimum_references=3)


def test_ranked_retrieval_fails_closed_on_invalid_contract():
    library = CreativeReferenceLibrary.load_default()
    with pytest.raises(ValueError, match="positive"):
        library.retrieve("horror", limit=0)
    with pytest.raises(ValueError, match="creator or work"):
        library.retrieve("horror", kind="unknown")


def test_optional_profile_lists_fail_closed_when_malformed():
    with pytest.raises(ValueError, match="optional reference list"):
        CreativeReferenceLibrary._optional_list({"techniques": "not-a-list"}, "techniques")
    with pytest.raises(ValueError, match="duplicate values"):
        CreativeReferenceLibrary._optional_list({"techniques": ["Shape", "shape"]}, "techniques")


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
