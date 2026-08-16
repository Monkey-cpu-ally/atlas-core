from creative_production.visual_quality import VisualQualityDirector


def scores(value=98):
    return {dimension: value for dimension in VisualQualityDirector.DIMENSIONS}


def test_master_quality_asset_passes():
    result = VisualQualityDirector().assess(
        observations=["Clean anatomy, coherent perspective, intentional lighting, faithful approved design."],
        scores=scores(),
    )
    assert result.production_ready
    assert result.violations == []


def test_hand_or_face_defect_hard_blocks_asset():
    result = VisualQualityDirector().assess(
        observations=["Extra fingers and warped face visible in final frame."],
        scores=scores(),
    )
    assert not result.production_ready
    assert "hand_defect" in result.violations
    assert "face_defect" in result.violations


def test_identity_drift_blocks_even_when_other_scores_are_high():
    quality = scores()
    quality["identity_consistency"] = 80
    result = VisualQualityDirector().assess(
        observations=["Identity drift from approved character master."], scores=quality
    )
    assert not result.production_ready
    assert "hard_quality_failure:identity_consistency" in result.violations
    assert "identity_drift" in result.violations


def test_generic_ai_look_warns_but_strict_scores_still_control_gate():
    result = VisualQualityDirector().assess(
        observations=["Technically clean but carries a generic AI and plastic skin appearance."], scores=scores()
    )
    assert result.production_ready
    assert "generic_generated_look" in result.warnings
    assert "synthetic_material_look" in result.warnings


def test_low_resolution_is_never_master_asset_ready():
    quality = scores()
    quality["resolution_fidelity"] = 70
    result = VisualQualityDirector().assess(observations=["Low resolution final asset."], scores=quality)
    assert not result.production_ready
    assert "hard_quality_failure:resolution_fidelity" in result.violations
    assert "insufficient_resolution" in result.violations
