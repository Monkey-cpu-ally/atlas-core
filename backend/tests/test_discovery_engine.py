from services import discovery_approval_pipeline as approval
from services import discovery_engine as engine


def setup_function():
    engine.reset_in_memory_state(); approval.reset_in_memory_state()


def test_investigation_starts_as_concept_and_frontier():
    record=engine.create_investigation(title="Low-temperature structural composite",question="Can a layered composite improve impact resistance without increasing mass?",subjects=["Materials Science","Physics"])
    assert record["status"]=="CONCEPT"; assert record["knowledge_layer"]=="FRONTIER"; assert record["evidence_score"]["score"]==0
    assert record["analogies"]==[]; assert record["candidate_hypotheses"]==[]; assert record["challenges"]==[]; assert record["prior_art_assessments"]==[]


def test_frontier_map_is_scoped_and_truthful():
    engine.create_investigation(title="Thermal question",question="Can geometry improve cooling?",knowledge_layer="FRONTIER",subjects=["Physics"])
    engine.create_investigation(title="Unknown biology",question="What mechanism explains the observation?",knowledge_layer="UNKNOWN",subjects=["Biology"])
    mapped=engine.map_frontier(subjects=["Physics"])
    assert mapped["counts"]["FRONTIER"]==1; assert mapped["counts"]["UNKNOWN"]==0; assert "tracking labels" in mapped["rule"]


def test_gap_detector_exposes_missing_verification_work():
    record=engine.create_investigation(title="Gap test",question="Can this effect be measured?")
    gaps=engine.detect_gaps(record["investigation_id"]); kinds={g["kind"] for g in gaps["gaps"]}
    assert {"foundation","question_decomposition","hypothesis","prior_art","evidence","experiment"}.issubset(kinds); assert gaps["ready_for_verified_claim"] is False


def test_cross_disciplinary_analogy_does_not_claim_feasibility():
    record=engine.create_investigation(title="Bio-inspired cooling",question="Can branching geometry improve passive cooling?",subjects=["Biology","Engineering"]); iid=record["investigation_id"]
    analogy=engine.add_analogy(iid,source_subject="Biology",target_subject="Engineering",source_concept="vascular branching",mechanism="branching distributes transport paths",transferable_principle="hierarchical branching may distribute flow across an area",constraints=["fluid properties differ","manufacturing imposes minimum channel size"],source_refs=[{"citation":"reviewed source"}])
    assert analogy["status"]=="candidate"; assert analogy["proves_feasibility"] is False; assert engine.get_investigation(iid)["status"]=="CONCEPT"


def _candidate(iid):
    analogy=engine.add_analogy(iid,source_subject="Biology",target_subject="Thermal Engineering",source_concept="vascular networks",mechanism="distributed transport",transferable_principle="branching can shorten transport paths",constraints=[])
    return engine.generate_candidate_hypothesis(iid,analogy_id=analogy["analogy_id"],statement="A branching channel layout reduces peak temperature by at least 5 percent under matched load.",rationale="The analogy suggests shorter distributed transport paths.",assumptions=["equal material mass","equal heat input"],falsification_criteria=["Peak temperature reduction is below 5 percent."],expected_observations=["lower peak temperature"],target_measurements=["peak_temperature_c"])


def test_candidate_hypothesis_requires_review_before_activation():
    record=engine.create_investigation(title="Analogy review",question="Can branching reduce thermal gradients?"); iid=record["investigation_id"]
    candidate=_candidate(iid)
    assert candidate["status"]=="pending_review"; assert engine.get_investigation(iid)["hypotheses"]==[]; assert engine.get_investigation(iid)["status"]=="CONCEPT"
    accepted=engine.accept_candidate_hypothesis(iid,candidate["candidate_id"])
    assert accepted["origin_candidate_id"]==candidate["candidate_id"]; assert engine.get_investigation(iid)["status"]=="HYPOTHESIS"; assert candidate["status"]=="accepted"


def test_challenge_gate_records_assumptions_and_conflicts_without_changing_truth_status():
    record=engine.create_investigation(title="Challenge review",question="Can the hypothesis survive contradictory evidence?"); iid=record["investigation_id"]
    hypothesis=engine.add_hypothesis(iid,statement="Geometry A lowers temperature.",rationale="It increases effective transport area.",falsification_criteria=["No measurable reduction."],assumptions=["airflow is equal"])
    challenge=engine.challenge_active_hypothesis(iid,hypothesis_id=hypothesis["hypothesis_id"],supporting_claims=[{"claim":"one supporting study"}],conflicting_claims=[{"claim":"a matched study found no effect","source_ref":"study-2"}])
    assert challenge["status"]=="CONTRADICTION_REVIEW_REQUIRED"; assert challenge["conflict_count"]==1
    assert engine.get_investigation(iid)["status"]=="HYPOTHESIS"; assert engine.get_investigation(iid)["challenges"][0]["hypothesis_id"]==hypothesis["hypothesis_id"]


def test_prior_art_no_match_never_claims_novelty():
    record=engine.create_investigation(title="Novelty review",question="Is the candidate actually novel?"); iid=record["investigation_id"]
    candidate=_candidate(iid)
    assessment=engine.assess_candidate_prior_art(iid,candidate_id=candidate["candidate_id"],search_queries=["branching thermal channel geometry"],matches=[])
    assert assessment["disposition"]=="NO_MATCH_RECORDED"; assert "not proof of novelty" in assessment["claim_rule"]
    assert candidate["novelty_status"]=="unproven"; assert engine.get_investigation(iid)["status"]=="CONCEPT"


def test_direct_prior_art_blocks_candidate_novelty_without_mutating_investigation_to_verified():
    record=engine.create_investigation(title="Direct prior art",question="Does direct prior art exist?"); iid=record["investigation_id"]
    candidate=_candidate(iid)
    assessment=engine.assess_candidate_prior_art(iid,candidate_id=candidate["candidate_id"],search_queries=["branching thermal channel"],matches=[{"title":"Existing branching cooler","source_ref":"patent-1","similarity":"DIRECT"}])
    assert assessment["disposition"]=="NOT_NOVEL_CANDIDATE"; assert candidate["novelty_status"]=="blocked_by_direct_prior_art"
    assert engine.get_investigation(iid)["status"]=="CONCEPT"


def test_same_subject_analogy_is_rejected():
    record=engine.create_investigation(title="Bad analogy",question="Does this transfer disciplines?")
    try: engine.add_analogy(record["investigation_id"],source_subject="Physics",target_subject="Physics",source_concept="waves",mechanism="oscillation",transferable_principle="frequency response",constraints=[])
    except engine.DiscoveryEngineError as exc: assert "different source and target" in str(exc)
    else: raise AssertionError("same-subject analogy must fail")


def test_hypothesis_requires_falsification_criteria():
    record=engine.create_investigation(title="Test",question="Can this measurable effect be reproduced?")
    try: engine.add_hypothesis(record["investigation_id"],statement="The effect exists.",rationale="A measurable signal was reported.",falsification_criteria=[])
    except engine.DiscoveryEngineError as exc: assert "falsification" in str(exc)
    else: raise AssertionError("hypothesis without falsification criteria must fail")


def test_discovery_lifecycle_promotes_to_existing_approval_pipeline():
    record=engine.create_investigation(title="Adaptive cooling geometry",question="Does geometry A remove heat faster than geometry B under equal load?",owner_ai="Hermes",subjects=["Engineering","Physics"],related_projects=["Weaver"]); iid=record["investigation_id"]
    hypothesis=engine.add_hypothesis(iid,statement="Geometry A lowers steady-state temperature by at least 5 percent.",rationale="It exposes more effective surface area to airflow.",falsification_criteria=["Temperature reduction is below 5 percent under matched conditions."],assumptions=["Airflow and heat input are held constant."])
    assert hypothesis["hypothesis_id"].startswith("HYP-"); assert engine.get_investigation(iid)["status"]=="HYPOTHESIS"
    engine.add_prior_art(iid,items=[{"title":"Comparable heat sink study","source_type":"peer_reviewed","url":"https://example.test/study"}],conclusion="Related approaches exist, but the exact geometry requires direct comparison.")
    engine.add_evidence(iid,evidence=[{"source_type":"peer_reviewed","citation":"Comparable heat sink study","direct_support":True}])
    engine.set_experiment_plan(iid,objective="Compare steady-state thermal performance.",method=["Apply equal heat load","Hold airflow constant","Record temperature"],measurements=["steady_state_temperature_c"],pass_fail_criteria=["Geometry A is at least 5 percent cooler than B"],safety_constraints=["Do not exceed material temperature rating"])
    draft=engine.promote_to_approval(iid)
    assert draft["status"]=="draft"; assert draft["owner_ai"]=="Hermes"; assert draft["discovery_engine_investigation_id"]==iid
    assert engine.get_investigation(iid)["approval_discovery_id"]==draft["discovery_id"]; assert approval.get_draft(draft["discovery_id"]) is draft


def test_simulation_is_not_physical_verification_and_gap_remains():
    record=engine.create_investigation(title="Simulation boundary",question="Does the model predict the expected response?"); iid=record["investigation_id"]
    engine.add_hypothesis(iid,statement="The model predicts a bounded response.",rationale="The governing equations impose a finite limit.",falsification_criteria=["The solver produces an unbounded response in the defined domain."])
    engine.set_experiment_plan(iid,objective="Run the numerical model.",method=["Execute solver"],measurements=["peak_response"],pass_fail_criteria=["Peak response remains below the defined limit"])
    result=engine.record_result(iid,result_type="simulation",summary="The numerical model remained bounded.",measurements={"peak_response":0.81},resulting_status="SIMULATED")
    assert result["status"]=="SIMULATED"; assert engine.get_investigation(iid)["status"]!="INDEPENDENTLY_VERIFIED"
    assert "physical_validation" in {g["kind"] for g in engine.detect_gaps(iid)["gaps"]}


def test_invalid_knowledge_layer_fails_truthfully():
    try: engine.create_investigation(title="Bad layer",question="Is this layer allowed?",knowledge_layer="MAGIC")
    except engine.DiscoveryEngineError as exc: assert "invalid knowledge_layer" in str(exc)
    else: raise AssertionError("invalid knowledge layer must fail")
