import json
from pathlib import Path
import pytest
from creative_intelligence.reference_library.loader import CreativeReference, CreativeReferenceLibrary
LIBRARY_DIR=Path(__file__).parents[1]/"creative_intelligence"/"reference_library"
def test_default_library_loads_seed_catalogs():
    s=CreativeReferenceLibrary.load_default().stats(); assert s["creators"]>=53; assert s["works"]>=35; assert s["total"]==s["creators"]+s["works"]; assert s["profiled"]>=21
def test_reference_ids_are_unique_and_retrievable():
    library=CreativeReferenceLibrary.load_default(); ids=[r.reference_id for r in library.all()]; assert len(ids)==len(set(ids)); assert all(library.get(r.reference_id)==r for r in library.all())
def test_profile_schema_is_backward_compatible():
    r=CreativeReference("creator:test","Test","creator","art",("composition",)); assert r.disciplines==r.techniques==r.strengths==r.study_targets==r.limitations==r.provenance==r.relationships==()
def test_search_matches_title_category_and_craft_principles():
    l=CreativeReferenceLibrary.load_default(); assert any(r.title=="Genndy Tartakovsky" for r in l.search("minimal dialogue")); assert any(r.title=="Bloodborne" for r in l.search("cosmic-horror")); assert any(r.kind=="creator" for r in l.search("literature"))
def test_ranked_retrieval_exposes_score_and_matching_terms():
    m=CreativeReferenceLibrary.load_default().retrieve("minimal dialogue visual storytelling",limit=5); assert m and all(x.score>0 and x.matched_terms for x in m); assert list(m)==sorted(m,key=lambda x:(-x.score,x.reference.title.casefold(),x.reference.reference_id))
def test_ranked_retrieval_can_filter_creator_and_work():
    l=CreativeReferenceLibrary.load_default(); c=l.retrieve("horror",kind="creator"); w=l.retrieve("horror",kind="work"); assert c and all(m.reference.kind=="creator" for m in c); assert w and all(m.reference.kind=="work" for m in w)
def test_ranked_retrieval_uses_deep_profile_fields():
    r=CreativeReference("creator:test","Test Creator","creator","design",("composition",),disciplines=("industrial design",),techniques=("functional silhouette",),strengths=("readability",),study_targets=("vehicle architecture",),limitations=("do not imitate signature forms",),provenance=("curated editorial profile",),relationships=("environment design",)); l=CreativeReferenceLibrary([r]); m=l.retrieve("vehicle architecture")[0]; assert m.reference==r; assert {"vehicle","architecture"}.issubset(set(m.matched_terms)); assert l.search("functional silhouette")== (r,)
def test_synthesis_combines_multiple_references_and_preserves_boundaries():
    s=CreativeReferenceLibrary.load_default().synthesize("minimal dialogue visual storytelling",limit=4); assert len(s.references)>=2; assert s.principles and s.study_targets and s.limitations and s.provenance; assert len(s.principles)==len({v.casefold() for v in s.principles}); assert any("do not" in v.casefold() for v in s.limitations)
def test_synthesis_is_deterministic_for_same_query():
    l=CreativeReferenceLibrary.load_default(); assert l.synthesize("industrial science fiction design",limit=4)==l.synthesize("industrial science fiction design",limit=4)
def test_synthesis_uses_identity_but_never_constraints_as_retrieval_context():
    refs=[CreativeReference("creator:visual","Visual","creator","animation",("minimal dialogue",)),CreativeReference("work:industrial","Industrial","work","film",("industrial science fiction",)),CreativeReference("work:gore","Gore","work","horror",("gore",))]; l=CreativeReferenceLibrary(refs); s=l.synthesize("minimal dialogue",limit=2,project_identity="industrial science fiction",project_constraints=("no gore",)); ids={m.reference.reference_id for m in s.references}; assert "creator:visual" in ids and "work:industrial" in ids; assert "work:gore" not in ids; assert s.project_constraints==("no gore",)
def test_project_constraints_fail_closed_instead_of_silent_cleanup():
    l=CreativeReferenceLibrary.load_default()
    with pytest.raises(ValueError,match="list of strings"): l.synthesize("visual storytelling",project_constraints="no gore")
    with pytest.raises(ValueError,match="non-empty strings"): l.synthesize("visual storytelling",project_constraints=("no gore",""))
    with pytest.raises(ValueError,match="duplicate project constraints"): l.synthesize("visual storytelling",project_constraints=("No Gore","no gore"))
def test_synthesis_prefers_distinct_reference_dimensions_before_rank_fill():
    refs=[CreativeReference("creator:a","A","creator","animation",("visual","storytelling")),CreativeReference("creator:b","B","creator","animation",("visual",)),CreativeReference("work:c","C","work","film",("visual",)),CreativeReference("creator:d","D","creator","design",("visual",))]; s=CreativeReferenceLibrary(refs).synthesize("visual storytelling",limit=3); assert len(s.references)==3; assert len(s.diversity_dimensions)==3; assert {"creator:animation","work:film","creator:design"}.issubset(set(s.diversity_dimensions))
def test_synthesis_fails_closed_without_reference_diversity():
    l=CreativeReferenceLibrary([CreativeReference("creator:one","One","creator","design",("shape",))])
    with pytest.raises(ValueError,match="insufficient references"): l.synthesize("shape")
    with pytest.raises(ValueError,match="at least two references"): l.synthesize("shape",minimum_references=1)
    with pytest.raises(ValueError,match="limit must meet minimum"): l.synthesize("shape",limit=2,minimum_references=3)
def test_ranked_retrieval_fails_closed_on_invalid_contract():
    l=CreativeReferenceLibrary.load_default()
    with pytest.raises(ValueError,match="positive"): l.retrieve("horror",limit=0)
    with pytest.raises(ValueError,match="creator or work"): l.retrieve("horror",kind="unknown")
def test_optional_profile_lists_fail_closed_when_malformed():
    with pytest.raises(ValueError,match="optional reference list"): CreativeReferenceLibrary._optional_list({"techniques":"not-a-list"},"techniques")
    with pytest.raises(ValueError,match="duplicate values"): CreativeReferenceLibrary._optional_list({"techniques":["Shape","shape"]},"techniques")
def test_catalogs_declare_originality_and_provenance_rules():
    c=json.loads((LIBRARY_DIR/"creative_masters.json").read_text(encoding="utf-8")); w=json.loads((LIBRARY_DIR/"works_catalog.json").read_text(encoding="utf-8")); rules=" ".join(c.get("rules",[])).lower(); purpose=f"{c.get('purpose','')} {w.get('purpose','')}".lower(); assert "provenance" in rules; assert "reject direct imitation" in rules; assert "never" in purpose and ("clone" in purpose or "reproduce" in purpose)
def test_loader_fails_closed_on_duplicate_reference_ids():
    first=CreativeReferenceLibrary.load_default().all()[0]
    with pytest.raises(ValueError,match="duplicate creative reference id"): CreativeReferenceLibrary([first,first])
