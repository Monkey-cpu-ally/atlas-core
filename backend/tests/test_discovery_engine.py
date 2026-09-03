from services import discovery_approval_pipeline as approval
from services import discovery_engine as engine
from services import invention_ledger


def setup_function():
    engine.reset_in_memory_state(); approval.reset_in_memory_state(); invention_ledger.reset_in_memory_state()


def _new(title="Ledger test", question="Can this claim be tested?"):
    return engine.create_investigation(title=title,question=question,subjects=["Engineering"])


def _candidate(iid):
    analogy=engine.add_analogy(iid,source_subject="Biology",target_subject="Thermal Engineering",source_concept="vascular networks",mechanism="distributed transport",transferable_principle="branching can shorten transport paths",constraints=[])
    return engine.generate_candidate_hypothesis(iid,analogy_id=analogy["analogy_id"],statement="A branching channel layout reduces peak temperature by at least 5 percent under matched load.",rationale="The analogy suggests shorter distributed transport paths.",assumptions=["equal material mass","equal heat input"],falsification_criteria=["Peak temperature reduction is below 5 percent."],expected_observations=["lower peak temperature"],target_measurements=["peak_temperature_c"])


def _design(iid,hypothesis_id):
    return engine.design_investigation_experiment(iid,hypothesis_id=hypothesis_id,independent_variables=["geometry"],dependent_variables=["temperature"],controls=["load"],procedure=["apply equal load"],pass_fail_criteria=["A lower than B"])


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
    record=_new(); gaps=engine.detect_gaps(record["investigation_id"]); kinds={g["kind"] for g in gaps["gaps"]}
    assert {"foundation","question_decomposition","hypothesis","prior_art","evidence","experiment"}.issubset(kinds); assert gaps["ready_for_verified_claim"] is False


def test_cross_disciplinary_analogy_does_not_claim_feasibility():
    record=_new(); iid=record["investigation_id"]
    analogy=engine.add_analogy(iid,source_subject="Biology",target_subject="Engineering",source_concept="vascular branching",mechanism="branching distributes transport paths",transferable_principle="hierarchical branching may distribute flow across an area",constraints=["fluid properties differ"])
    assert analogy["status"]=="candidate"; assert analogy["proves_feasibility"] is False; assert engine.get_investigation(iid)["status"]=="CONCEPT"


def test_candidate_hypothesis_requires_review_before_activation():
    record=_new(); iid=record["investigation_id"]; candidate=_candidate(iid)
    assert candidate["status"]=="pending_review"; assert engine.get_investigation(iid)["hypotheses"]==[]; assert engine.get_investigation(iid)["status"]=="CONCEPT"
    accepted=engine.accept_candidate_hypothesis(iid,candidate["candidate_id"])
    assert accepted["origin_candidate_id"]==candidate["candidate_id"]; assert engine.get_investigation(iid)["status"]=="HYPOTHESIS"; assert candidate["status"]=="accepted"


def test_challenge_gate_records_conflict_without_changing_truth_status():
    record=_new(); iid=record["investigation_id"]
    hypothesis=engine.add_hypothesis(iid,statement="Geometry A lowers temperature.",rationale="It increases effective transport area.",falsification_criteria=["No measurable reduction."],assumptions=["airflow is equal"])
    challenge=engine.challenge_active_hypothesis(iid,hypothesis_id=hypothesis["hypothesis_id"],supporting_claims=[],conflicting_claims=[{"claim":"matched study found no effect"}])
    assert challenge["conflict_count"]==1; assert challenge["resolution_status"]=="UNRESOLVED"; assert challenge["challenge_id"].startswith("CHL-")
    assert engine.get_investigation(iid)["status"]=="HYPOTHESIS"


def test_unresolved_contradiction_blocks_experiment_design_and_is_reported_as_gap():
    record=_new(); iid=record["investigation_id"]
    hyp=engine.add_hypothesis(iid,statement="A produces less heat than B.",rationale="Lower resistance is expected.",falsification_criteria=["Measured heat is not lower."],assumptions=["same load"])
    engine.challenge_active_hypothesis(iid,hypothesis_id=hyp["hypothesis_id"],supporting_claims=[],conflicting_claims=[{"claim":"prior test disagrees"}])
    assert "contradiction" in {g["kind"] for g in engine.detect_gaps(iid)["gaps"]}
    try: _design(iid,hyp["hypothesis_id"])
    except engine.DiscoveryEngineError as exc: assert "unresolved contradiction" in str(exc)
    else: raise AssertionError("unresolved contradiction must block design")


def test_resolved_contradiction_with_evidence_can_advance_to_experiment_design():
    record=_new(); iid=record["investigation_id"]
    hyp=engine.add_hypothesis(iid,statement="A produces less heat than B.",rationale="Lower resistance is expected.",falsification_criteria=["Measured heat is not lower."],assumptions=["same load"])
    challenge=engine.challenge_active_hypothesis(iid,hypothesis_id=hyp["hypothesis_id"],supporting_claims=[],conflicting_claims=[{"claim":"prior test disagrees"}])
    resolved=engine.resolve_challenge(iid,challenge["challenge_id"],resolution="RESOLVED",resolution_note="Matched calibration data explains the apparent conflict.",evidence_refs=["study-2-calibration"],resolved_by="Minerva")
    assert resolved["resolution_status"]=="RESOLVED"; assert "contradiction" not in {g["kind"] for g in engine.detect_gaps(iid)["gaps"]}
    design=_design(iid,hyp["hypothesis_id"]); assert design["hypothesis_id"]==hyp["hypothesis_id"]
    ledger=engine.get_invention_ledger(iid); assert any(e["event_type"]=="REVISION" and e["payload"].get("challenge_id")==challenge["challenge_id"] for e in ledger["events"])


def test_resolved_contradiction_requires_evidence_references():
    record=_new(); iid=record["investigation_id"]
    hyp=engine.add_hypothesis(iid,statement="A produces less heat than B.",rationale="Lower resistance is expected.",falsification_criteria=["Measured heat is not lower."])
    challenge=engine.challenge_active_hypothesis(iid,hypothesis_id=hyp["hypothesis_id"],supporting_claims=[],conflicting_claims=[{"claim":"prior test disagrees"}])
    try: engine.resolve_challenge(iid,challenge["challenge_id"],resolution="RESOLVED",resolution_note="Conflict resolved.")
    except engine.DiscoveryEngineError as exc: assert "evidence references" in str(exc)
    else: raise AssertionError("resolved contradiction must require evidence")


def test_invalidated_challenge_invalidates_hypothesis_and_blocks_design():
    record=_new(); iid=record["investigation_id"]
    hyp=engine.add_hypothesis(iid,statement="A produces less heat than B.",rationale="Lower resistance is expected.",falsification_criteria=["Measured heat is not lower."])
    challenge=engine.challenge_active_hypothesis(iid,hypothesis_id=hyp["hypothesis_id"],supporting_claims=[],conflicting_claims=[{"claim":"decisive contrary measurement"}])
    engine.resolve_challenge(iid,challenge["challenge_id"],resolution="INVALIDATED",resolution_note="Contrary measurement falsifies the active hypothesis.",evidence_refs=["measurement-7"])
    assert engine.get_investigation(iid)["status"]=="INVALIDATED"; assert hyp["status"]=="invalidated_by_challenge"
    try: _design(iid,hyp["hypothesis_id"])
    except engine.DiscoveryEngineError as exc: assert "active hypothesis" in str(exc)
    else: raise AssertionError("invalidated hypothesis must not advance")


def test_prior_art_no_match_never_claims_novelty_and_requires_explicit_review():
    record=_new(); iid=record["investigation_id"]; candidate=_candidate(iid)
    assessment=engine.assess_candidate_prior_art(iid,candidate_id=candidate["candidate_id"],search_queries=["branching thermal channel geometry"],matches=[])
    assert assessment["disposition"]=="NO_MATCH_RECORDED"; assert "not proof of novelty" in assessment["claim_rule"]; assert candidate["novelty_status"]=="unproven"
    assert assessment["review_status"]=="pending"; assert engine.get_investigation(iid)["status"]=="CONCEPT"
    accepted=engine.accept_prior_art_assessment(iid,assessment["assessment_id"],reviewer="Council",review_note="Search reviewed.")
    assert accepted["review_status"]=="accepted_no_direct_blocker"; assert engine.get_investigation(iid)["status"]=="PRIOR_ART_CHECKED"
    assert "Novelty is not proven" in engine.get_investigation(iid)["prior_art_conclusion"]


def test_direct_prior_art_blocks_candidate_and_prior_art_acceptance():
    record=_new(); iid=record["investigation_id"]; candidate=_candidate(iid)
    assessment=engine.assess_candidate_prior_art(iid,candidate_id=candidate["candidate_id"],search_queries=["branching thermal channel"],matches=[{"title":"Existing branching cooler","similarity":"DIRECT"}])
    try: engine.accept_candidate_hypothesis(iid,candidate["candidate_id"])
    except engine.DiscoveryEngineError as exc: assert "blocked by direct prior art" in str(exc)
    else: raise AssertionError("direct prior art must block candidate acceptance")
    try: engine.accept_prior_art_assessment(iid,assessment["assessment_id"])
    except engine.DiscoveryEngineError as exc: assert "direct prior art" in str(exc)
    else: raise AssertionError("direct prior art must not pass review")


def test_close_prior_art_remains_unresolved_and_cannot_pass_review():
    record=_new(); iid=record["investigation_id"]; candidate=_candidate(iid)
    assessment=engine.assess_candidate_prior_art(iid,candidate_id=candidate["candidate_id"],search_queries=["branching thermal channel"],matches=[{"title":"Related branching cooler","similarity":"CLOSE"}])
    assert candidate["novelty_status"]=="unresolved"
    try: engine.accept_prior_art_assessment(iid,assessment["assessment_id"])
    except engine.DiscoveryEngineError as exc: assert "must be resolved" in str(exc)
    else: raise AssertionError("unresolved prior art must not pass review")


def test_evidence_evaluation_does_not_establish_truth():
    record=_new(); iid=record["investigation_id"]
    engine.add_evidence(iid,evidence=[{"source_type":"peer_reviewed","citation":"study","direct_support":True}])
    evaluation=engine.evaluate_investigation_evidence(iid)
    assert evaluation["disposition"] in {"INSUFFICIENT_EVIDENCE","MODERATE_EVIDENCE_FOR_REVIEW","STRONG_EVIDENCE_FOR_REVIEW"}; assert engine.get_investigation(iid)["status"]!="INDEPENDENTLY_VERIFIED"


def test_simulation_cannot_masquerade_as_experimental_support():
    record=_new(); iid=record["investigation_id"]
    engine.add_hypothesis(iid,statement="Model remains stable.",rationale="Equations are bounded.",falsification_criteria=["Solver diverges."])
    engine.set_experiment_plan(iid,objective="run model",method=["simulate"],measurements=["stability"],pass_fail_criteria=["bounded"])
    try: engine.record_result(iid,result_type="simulation",summary="bounded",resulting_status="EXPERIMENTALLY_SUPPORTED")
    except engine.DiscoveryEngineError as exc: assert "simulation cannot" in str(exc)
    else: raise AssertionError("simulation must not masquerade as experimental support")


def test_independent_simulation_replication_never_becomes_physical_verification():
    record=_new(); iid=record["investigation_id"]
    hyp=engine.add_hypothesis(iid,statement="Device remains below 70 C.",rationale="Thermal model predicts adequate dissipation.",falsification_criteria=["Temperature reaches 70 C."])
    _design(iid,hyp["hypothesis_id"])
    result=engine.record_result(iid,result_type="simulation",summary="Model predicts 62 C.",measurements={"temperature_c":62},resulting_status="SIMULATED")
    replication=engine.record_replication(iid,original_result_id=result["result_id"],replication_runs=[{"outcome":"supports","independent":True,"run_type":"simulation"},{"outcome":"supports","independent":True,"run_type":"simulation"}],required_successes=2,independent_required=True,verification_context="physical")
    assert replication["status"]=="REPLICATED"; assert replication["independent_support_count"]==0; assert engine.detect_gaps(iid)["ready_for_verified_claim"] is False
    kinds=[e["event_type"] for e in engine.get_invention_ledger(iid)["events"]]; assert "REPLICATION" in kinds; assert "INDEPENDENT_VERIFICATION" not in kinds


def test_replication_states_cannot_be_manually_asserted():
    record=_new(); iid=record["investigation_id"]
    engine.add_hypothesis(iid,statement="Effect exists.",rationale="Preliminary signal.",falsification_criteria=["No signal."])
    engine.set_experiment_plan(iid,objective="measure",method=["measure"],measurements=["signal"],pass_fail_criteria=["signal > threshold"])
    try: engine.record_result(iid,result_type="experiment",summary="caller assertion",resulting_status="INDEPENDENTLY_VERIFIED")
    except engine.DiscoveryEngineError as exc: assert "replication manager" in str(exc)
    else: raise AssertionError("independent verification must come through replication manager")


def test_promotion_requires_reviewed_prior_art_then_hands_off_to_approval_pipeline():
    record=engine.create_investigation(title="Adaptive cooling geometry",question="Does geometry A remove heat faster than geometry B under equal load?",owner_ai="Hermes",subjects=["Engineering","Physics"],related_projects=["Weaver"]); iid=record["investigation_id"]
    candidate=_candidate(iid); engine.accept_candidate_hypothesis(iid,candidate["candidate_id"])
    assessment=engine.assess_candidate_prior_art(iid,candidate_id=candidate["candidate_id"],search_queries=["adaptive cooling geometry"],matches=[])
    try: engine.promote_to_approval(iid)
    except engine.DiscoveryEngineError as exc: assert "not ready" in str(exc) or "prior-art" in str(exc)
    else: raise AssertionError("unreviewed prior art must block approval promotion")
    engine.accept_prior_art_assessment(iid,assessment["assessment_id"],reviewer="Council",review_note="Reviewed search coverage.")
    draft=engine.promote_to_approval(iid)
    assert draft["status"]=="draft"; assert draft["owner_ai"]=="Hermes"; assert draft["discovery_engine_investigation_id"]==iid


def test_investigation_creates_linked_ledger_with_question_event():
    record=_new(); ledger=engine.get_invention_ledger(record["investigation_id"])
    assert record["ledger_id"]==ledger["ledger_id"]; assert ledger["events"][0]["event_type"]=="QUESTION"; assert "does not prove novelty" in ledger["claim_rule"]
    assert engine.verify_invention_ledger(record["investigation_id"])["valid"] is True


def test_tampering_is_detected_by_engine_ledger_verification():
    record=_new(); iid=record["investigation_id"]; ledger=engine.get_invention_ledger(iid); ledger["events"][0]["payload"]["question"]="tampered after recording"
    check=engine.verify_invention_ledger(iid); assert check["valid"] is False; assert check["broken_at"]==0


def test_invalid_knowledge_layer_fails_truthfully():
    try: engine.create_investigation(title="Bad layer",question="Is this layer allowed?",knowledge_layer="MAGIC")
    except engine.DiscoveryEngineError as exc: assert "invalid knowledge_layer" in str(exc)
    else: raise AssertionError("invalid knowledge layer must fail")
