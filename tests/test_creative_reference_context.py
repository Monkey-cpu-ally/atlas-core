import pytest
from creative_intelligence.reference_context import ReferenceContext


def valid_context():
    return {
        "query":"visual storytelling",
        "project_identity":"Original machine-world family drama",
        "project_constraints":["no gore","functional machinery"],
        "diversity_dimensions":["creator:animation","work:film"],
        "reference_ids":["creator:test","work:test"],
        "principles":["strong silhouettes","visual clarity"],
        "study_targets":["staging"],
        "limitations":["do not imitate distinctive expression"],
        "provenance":["curated creator profile","curated work profile"],
        "contract":{
            "principle_only":True,
            "project_identity_overrides_reference_influence":True,
            "project_constraints_preserved":True,
            "constraints_are_not_inspiration":True,
        },
    }


def test_reference_context_accepts_safe_canonical_contract():
    context=ReferenceContext.from_mapping(valid_context())
    assert context.project_identity=="Original machine-world family drama"
    assert context.project_constraints==("no gore","functional machinery")
    assert context.reference_ids==("creator:test","work:test")


def test_reference_context_rejects_non_object_and_invalid_list_shapes():
    with pytest.raises(ValueError,match="must be an object"): ReferenceContext.from_mapping("bad")
    payload=valid_context(); payload["project_constraints"]="no gore"
    with pytest.raises(ValueError,match="project_constraints must be a list"): ReferenceContext.from_mapping(payload)
    payload=valid_context(); payload["principles"]=["visual clarity",7]
    with pytest.raises(ValueError,match="principles must contain non-empty strings"): ReferenceContext.from_mapping(payload)


def test_reference_context_rejects_duplicate_values_case_insensitively():
    payload=valid_context(); payload["project_constraints"]=["No Gore"," no gore "]
    with pytest.raises(ValueError,match="duplicate values.*project_constraints"): ReferenceContext.from_mapping(payload)


def test_reference_context_requires_principle_only_and_project_identity_authority():
    payload=valid_context(); payload["contract"]["principle_only"]=False
    with pytest.raises(ValueError,match="principle-only"): ReferenceContext.from_mapping(payload)
    payload=valid_context(); payload["contract"].pop("project_identity_overrides_reference_influence")
    with pytest.raises(ValueError,match="project identity authority"): ReferenceContext.from_mapping(payload)


def test_reference_context_requires_constraint_preservation_boundaries():
    payload=valid_context(); payload["contract"]["project_constraints_preserved"]=False
    with pytest.raises(ValueError,match="preserve project constraints"): ReferenceContext.from_mapping(payload)
    payload=valid_context(); payload["contract"]["constraints_are_not_inspiration"]=False
    with pytest.raises(ValueError,match="constraints must not be inspiration"): ReferenceContext.from_mapping(payload)


def test_reference_context_rejects_legacy_constraint_retrieval_behavior():
    payload=valid_context(); payload["contract"]["project_constraints_applied_to_retrieval"]=True
    with pytest.raises(ValueError,match="must never be applied to reference retrieval"): ReferenceContext.from_mapping(payload)


def test_reference_context_requires_provenance_for_references():
    payload=valid_context(); payload["provenance"]=[]
    with pytest.raises(ValueError,match="requires provenance"): ReferenceContext.from_mapping(payload)


def test_empty_reference_context_means_no_reference_intelligence():
    assert ReferenceContext.from_mapping(None) is None
    assert ReferenceContext.from_mapping({}) is None
