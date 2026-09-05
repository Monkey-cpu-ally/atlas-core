from services import discovery_challenge as challenge


def test_assumptions_are_made_explicit():
    result=challenge.challenge_hypothesis(statement="A transfers to B",assumptions=["scale effects are negligible"],supporting_claims=[],conflicting_claims=[])
    assert result["status"]=="ASSUMPTIONS_EXPOSED"
    assert result["challenges"][0]["type"]=="ASSUMPTION"
    assert "does not prove" in result["claim_rule"]


def test_conflicting_evidence_requires_resolution():
    result=challenge.challenge_hypothesis(statement="A improves B",assumptions=[],supporting_claims=[{"claim":"support"}],conflicting_claims=[{"claim":"A reduced B in a comparable test","source_ref":"SRC-1"}])
    assert result["status"]=="CONTRADICTION_REVIEW_REQUIRED"
    assert result["conflict_count"]==1
    assert result["challenges"][0]["resolution_required"] is True


def test_direct_prior_art_blocks_novelty_candidate():
    result=challenge.assess_prior_art(candidate_statement="candidate",search_queries=["candidate mechanism"],matches=[{"title":"Earlier work","similarity":"DIRECT","source_ref":"DOI:test"}])
    assert result["disposition"]=="NOT_NOVEL_CANDIDATE"
    assert result["strongest_match"]=="DIRECT"


def test_no_recorded_match_does_not_claim_novelty():
    result=challenge.assess_prior_art(candidate_statement="candidate",search_queries=["candidate mechanism"],matches=[])
    assert result["disposition"]=="NO_MATCH_RECORDED"
    assert "not proof of novelty" in result["claim_rule"]
