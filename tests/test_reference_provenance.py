from creative_production.reference_provenance import ReferenceInfluence, ReferenceProvenanceDirector


def influence(ref, title, principle, contribution):
    return ReferenceInfluence(ref, title, "animation", [principle], contribution)


def test_multiple_references_can_contribute_principles_without_cloning():
    influences = [
        influence("ref-a", "Reference A", "silhouette readability", "use clearer silhouettes"),
        influence("ref-b", "Reference B", "restrained dialogue", "allow visual acting to carry scenes"),
        influence("ref-c", "Reference C", "environmental scale", "increase scale contrast in original locations"),
    ]
    result = ReferenceProvenanceDirector().assess(
        influences=influences,
        similarity_scores={"ref-a": .31, "ref-b": .22, "ref-c": .28},
        output_notes=["New composition, new characters, new setting, principles transformed for project identity."],
    )
    assert result.passes


def test_close_similarity_to_one_reference_is_blocked():
    result = ReferenceProvenanceDirector().assess(
        influences=[influence("ref-a", "Reference A", "shape rhythm", "adapt rhythm to original design")],
        similarity_scores={"ref-a": .86},
    )
    assert not result.passes
    assert "reference_similarity_too_high:ref-a" in result.violations


def test_direct_copy_instruction_is_blocked():
    result = ReferenceProvenanceDirector().assess(
        influences=[influence("ref-a", "Reference A", "lighting contrast", "study contrast")],
        similarity_scores={"ref-a": .2}, output_notes=["Copy exactly the reference composition."],
    )
    assert not result.passes
    assert "direct_imitation_instruction" in result.violations


def test_reference_must_record_principles_and_contribution():
    bad = ReferenceInfluence("ref-a", "Reference A", "film", [], "")
    result = ReferenceProvenanceDirector().assess(influences=[bad], similarity_scores={"ref-a": .1})
    assert not result.passes
    assert "missing_extracted_principles:ref-a" in result.violations
    assert "missing_contribution_record:ref-a" in result.violations
