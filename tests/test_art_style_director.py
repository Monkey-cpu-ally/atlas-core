from creative_production.art_style import ArtStyleBible, ArtStyleDirector


def bible():
    return ArtStyleBible(
        project="Night Band", shape_language="soft natural arcs contrasted with sharp danger shapes",
        silhouette_rules="characters readable in silhouette", anatomy_proportions="grounded stylization",
        line_edge_treatment="controlled hand-crafted edges", palette_logic="night blues with restrained luminous accents",
        lighting_philosophy="motivated moonlight and diegetic fairy glow", texture_material_language="tactile storybook surfaces",
        environment_architecture="old-world academy and mythic forest forms", facial_expression_language="restrained readable acting",
        composition_perspective="clear focal hierarchy and deliberate depth", detail_policy="detail supports focal hierarchy",
        animation_principles="strong poses, restraint, readable staging",
        forbidden_traits=["random neon", "plastic skin", "default anime"],
    )


def high_scores():
    return {dimension: 96 for dimension in ArtStyleDirector.DIMENSIONS}


def test_original_coherent_style_is_production_ready():
    result = ArtStyleDirector().assess(
        bible(), observations=["Distinct project identity; tactile surfaces; restrained luminous accents."], scores=high_scores()
    )
    assert result.production_ready
    assert result.violations == []


def test_generic_or_derivative_style_is_rejected():
    scores = high_scores()
    scores["originality"] = 72
    result = ArtStyleDirector().assess(
        bible(), observations=["Make it exactly like the reference with random neon and plastic skin."], scores=scores
    )
    assert not result.production_ready
    assert "derivative_reference_imitation" in result.violations
    assert "insufficient_visual_originality" in result.violations
    assert "forbidden_trait:random neon" in result.violations
    assert "forbidden_trait:plastic skin" in result.violations


def test_style_drift_is_hard_failure_even_with_high_average():
    scores = high_scores()
    scores["character_consistency"] = 70
    result = ArtStyleDirector().assess(bible(), observations=["Character rendering drifted from the approved master."], scores=scores)
    assert not result.production_ready
    assert "character_style_drift" in result.violations
