from services import discovery_approval_pipeline as approval
from services import discovery_engine as engine


def setup_function():
    engine.reset_in_memory_state(); approval.reset_in_memory_state()


def test_investigation_starts_as_concept_and_frontier():
    record=engine.create_investigation(title="Low-temperature structural composite",question="Can a layered composite improve impact resistance without increasing mass?",subjects=["Materials Science","Physics"])
    assert record["status"]=="CONCEPT"; assert record["knowledge_layer"]=="FRONTIER"; assert record["evidence_score"]["score"]==0
    assert record["analogies"]==[]; assert record["candidate_hypotheses"]==[]; assert record["challenges"]==[]; assert record["prior_art_assessments"]==[]
    assert record["experiment_designs"]==[]; assert record["evidence_evaluations"]==[]; assert record["replications"]==[]


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
    assert engine.get_investigation(iid)["status"]=="HYPOTHESIS"


def test_prior_art_no_match_never_claims_novelty():
    record=engine.create_investigation(title="Novelty review",question="Is the candidate actually novel?"); iid=record["investigation_id"]
    candidate=_candidate(iid)
    assessment=engine.assess_candidate_prior_art(iid,candidate_id=candidate["candidate_id"],search_queries=["branching thermal channel geometry"],matches=[])
    assert assessment["disposition"]=="NO_MATCH_RECORDED"; assert "not proof of novelty" in assessment["claim_rule"]
    assert candidate["novelty_status"]=="unproven"


def test_direct_prior_art_blocks_candidate_acceptance():
    record=engine.create_investigation(title="Direct prior art",question="Does direct prior art exist?"); iid=record["investigation_id"]
    candidate=_candidate(iid)
    engine.assess_candidate_prior_art(iid,candidate_id=candidate["candidate_id"],search_queries=["branching thermal channel"],matches=[{"title":"Existing branching cooler","source_ref":"patent-1","similarity":"DIRECT"}])
    try: engine.accept_candidate_hypothesis(iid,candidate["candidate_id"])
    except engine.DiscoveryEngineError as exc: assert "blocked by direct prior art" in str(exc)
    else: raise AssertionError("direct prior art must block candidate acceptance")


def test_experiment_design_requires_resolved_contradictions():
    record=engine.create_investigation(title="Contradiction gate",question="Can we test this safely?"); iid=record["investigation_id"]
    hyp=engine.add_hypothesis(iid,statement="A produces less heat than B.",rationale="Lower resistance is expected.",falsification_criteria=["Measured heat is not lower."],assumptions=["same load"])
    engine.challenge_active_hypothesis(iid,hypothesis_id=hyp["hypothesis_id"],supporting_claims=[],conflicting_claims=[{"claim":"prior test disagrees"}])
    try: engine.design_investigation_experiment(iid,hypothesis_id=hyp["hypothesis_id"],independent_variables=["geometry"],dependent_variables=["temperature"],controls=["load"],procedure=["apply equal load"],pass_fail_criteria=["A lower than B"])
    except engine.DiscoveryEngineError as exc: assert "unresolved contradiction" in str(exc)
    else: raise AssertionError("unresolved contradiction must block design")


def test_evidence_evaluation_does_not_establish_truth():
    record=engine.create_investigation(title="Evidence review",question="How strong is the evidence?"); iid=record["investigation_id"]
    engine.add_evidence(iid,evidence=[{"source_type":"peer_reviewed","citation":"study","direct_support":True}])
    evaluation=engine.evaluate_investigation_evidence(iid)
    assert evaluation["disposition"] in {"INSUFFICIENT_EVIDENCE","MODERATE_EVIDENCE_FOR_REVIEW","STRONG_EVIDENCE_FOR_REVIEW"}
    assert engine.get_investigation(iid)["status"]!="INDEPENDENTLY_VERIFIED"


def test_simulation_cannot_be_recorded_as_experimental_support():
    record=engine.create_investigation(title="Simulation truth",question="Can simulation be called experimental evidence?"); iid=record["investigation_id"]
    engine.add_hypothesis(iid,statement="The model remains stable.",rationale="The equations are bounded.",falsification_criteria=["Solver diverges."])
    engine.set_experiment_plan(iid,objective="Run model",method=["simulate"],measurements=["stability"],pass_fail_criteria=["bounded"])
    try: engine.record_result(iid,result_type="simulation",summary="bounded",resulting_status="EXPERIMENTALLY_SUPPORTED")
    except engine.DiscoveryEngineError as exc: assert "simulation cannot" in str(exc)
    else: raise AssertionError("simulation must not masquerade as experimental support")


def test_independent_simulation_replication_never_becomes_physical_verification():
    record=engine.create_investigation(title="Replication truth",question="Can independent simulations prove a physical claim?"); iid=record["investigation_id"]
    hyp=engine.add_hypothesis(iid,statement="Device remains below 70 C.",rationale="Thermal model predicts adequate dissipation.",falsification_criteria=["Temperature reaches 70 C."])
    engine.design_investigation_experiment(iid,hypothesis_id=hyp["hypothesis_id"],independent_variables=["load"],dependent_variables=["temperature"],controls=["ambient"],procedure=["run solver"],pass_fail_criteria=["temperature < 70 C"])
    result=engine.record_result(iid,result_type="simulation",summary="Model predicts 62 C.",measurements={"temperature_c":62},resulting_status="SIMULATED")
    replication=engine.record_replication(iid,original_result_id=result["result_id"],replication_runs=[{"outcome":"supports","independent":True,"run_type":"simulation"},{"outcome":"supports","independent":True,"run_type":"simulation"}],required_successes=2,independent_required=True,verification_context="physical")
    assert replication["status"]=="REPLICATED"; assert replication["independent_support_count"]==0
    assert engine.get_investigation(iid)["status"]=="REPLICATED"; assert engine.detect_gaps(iid)["ready_for_verified_claim"] is False


def test_replication_states_cannot_be_manually_asserted():
    record=engine.create_investigation(title="Manual status",question="Can a caller assert independent verification?"); iid=record["investigation_id"]
    engine.add_hypothesis(iid,statement="Effect exists.",rationale="Preliminary signal.",falsification_criteria=["No signal."])
    engine.set_experiment_plan(iid,objective="measure",method=["measure"],measurements=["signal"],pass_fail_criteria=["signal > threshold"])
    try: engine.record_result(iid,result_type="experiment",summary="caller assertion",resulting_status="INDEPENDENTLY_VERIFIED")
    except engine.DiscoveryEngineError as exc: assert "replication manager" in str(exc)
    else: raise AssertionError("independent verification must come through replication manager")


def test_discovery_lifecycle_promotes_to_existing_approval_pipeline():
    record=engine.create_investigation(title="Adaptive cooling geometry",question="Does geometry A remove heat faster than geometry B under equal load?",owner_ai="Hermes",subjects=["Engineering","Physics"],related_projects=["Weaver"]); iid=record["investigation_id"]
    engine.add_hypothesis(iid,statement="Geometry A lowers steady-state temperature by at least 5 percent.",rationale="It exposes more effective surface area to airflow.",falsification_criteria=["Temperature reduction is below 5 percent under matched conditions."],assumptions=["Airflow and heat input are held constant."])
    engine.add_prior_art(iid,items=[{"title":"Comparable heat sink study","source_type":"peer_reviewed","url":"https://example.test/study"}],conclusion="Related approaches exist, but the exact geometry requires direct comparison.")
    engine.add_evidence(iid,evidence=[{"source_type":"peer_reviewed","citation":"Comparable heat sink study","direct_support":True}])
    engine.set_experiment_plan(iid,objective="Compare steady-state thermal performance.",method=["Apply equal heat load","Hold airflow constant","Record temperature"],measurements=["steady_state_temperature_c"],pass_fail_criteria=["Geometry A is at least 5 percent cooler than B"],safety_constraints=["Do not exceed material temperature rating"])
    draft=engine.promote_to_approval(iid)
    assert draft["status"]=="draft"; assert draft["owner_ai"]=="Hermes"; assert draft["discovery_engine_investigation_id"]==iid


def test_invalid_knowledge_layer_fails_truthfully():
    try: engine.create_investigation(title="Bad layer",question="Is this layer allowed?",knowledge_layer="MAGIC")
    except engine.DiscoveryEngineError as exc: assert "invalid knowledge_layer" in str(exc)
    else: raise AssertionError("invalid knowledge layer must fail")
