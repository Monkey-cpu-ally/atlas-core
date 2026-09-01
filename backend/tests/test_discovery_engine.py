from services import discovery_approval_pipeline as approval
from services import discovery_engine as engine
from services import invention_ledger


def setup_function():
    engine.reset_in_memory_state(); approval.reset_in_memory_state(); invention_ledger.reset_in_memory_state()


def _new(title="Ledger test", question="Can this claim be tested?"):
    return engine.create_investigation(title=title,question=question,subjects=["Engineering"])


def test_investigation_creates_linked_ledger_with_question_event():
    record=_new(); ledger=engine.get_invention_ledger(record["investigation_id"])
    assert record["ledger_id"]==ledger["ledger_id"]
    assert ledger["investigation_id"]==record["investigation_id"]
    assert ledger["events"][0]["event_type"]=="QUESTION"
    assert "does not prove novelty" in ledger["claim_rule"]
    assert engine.verify_invention_ledger(record["investigation_id"])["valid"] is True


def test_discovery_lifecycle_writes_ordered_hash_chained_provenance():
    record=_new("Cooling provenance","Can geometry reduce peak temperature?"); iid=record["investigation_id"]
    analogy=engine.add_analogy(iid,source_subject="Biology",target_subject="Engineering",source_concept="vascular branching",mechanism="distributed transport",transferable_principle="branching may shorten transport paths",constraints=[])
    candidate=engine.generate_candidate_hypothesis(iid,analogy_id=analogy["analogy_id"],statement="Branching reduces peak temperature by 5 percent.",rationale="Shorter transport paths may improve distribution.",assumptions=["equal load"],falsification_criteria=["reduction below 5 percent"],expected_observations=["lower peak temperature"],target_measurements=["temperature_c"])
    hypothesis=engine.accept_candidate_hypothesis(iid,candidate["candidate_id"])
    engine.challenge_active_hypothesis(iid,hypothesis_id=hypothesis["hypothesis_id"],supporting_claims=[],conflicting_claims=[])
    engine.add_prior_art(iid,items=[{"title":"related study"}],conclusion="Related but not dispositive.")
    engine.add_evidence(iid,evidence=[{"source_type":"peer_reviewed","citation":"study","direct_support":True}])
    engine.set_experiment_plan(iid,objective="compare",method=["simulate"],measurements=["temperature_c"],pass_fail_criteria=["5 percent lower"])
    result=engine.record_result(iid,result_type="simulation",summary="model supports bounded reduction",measurements={"temperature_c":62},resulting_status="SIMULATED")
    engine.record_replication(iid,original_result_id=result["result_id"],replication_runs=[{"outcome":"supports","independent":True,"run_type":"simulation"},{"outcome":"supports","independent":True,"run_type":"simulation"}],verification_context="physical")
    ledger=engine.get_invention_ledger(iid); kinds=[event["event_type"] for event in ledger["events"]]
    assert kinds[0]=="QUESTION"
    for expected in ("ANALOGY","HYPOTHESIS","ASSUMPTION_CHALLENGE","PRIOR_ART","SOURCE","EXPERIMENT_PLAN","SIMULATION_RESULT","REPLICATION"):
        assert expected in kinds
    assert engine.verify_invention_ledger(iid)["event_count"]==len(ledger["events"])


def test_tampering_is_detected_by_engine_ledger_verification():
    record=_new(); iid=record["investigation_id"]
    engine.add_hypothesis(iid,statement="Effect exists.",rationale="A measurable signal is expected.",falsification_criteria=["No signal is measured."])
    ledger=engine.get_invention_ledger(iid); assert engine.verify_invention_ledger(iid)["valid"] is True
    ledger["events"][0]["payload"]["question"]="tampered after recording"
    check=engine.verify_invention_ledger(iid)
    assert check["valid"] is False; assert check["broken_at"]==0


def test_independent_simulation_is_logged_as_replication_not_independent_verification():
    record=_new(); iid=record["investigation_id"]
    engine.add_hypothesis(iid,statement="Device stays below 70 C.",rationale="Model predicts adequate cooling.",falsification_criteria=["Temperature reaches 70 C."])
    engine.set_experiment_plan(iid,objective="model",method=["simulate"],measurements=["temperature_c"],pass_fail_criteria=["below 70 C"])
    result=engine.record_result(iid,result_type="simulation",summary="62 C",resulting_status="SIMULATED")
    replication=engine.record_replication(iid,original_result_id=result["result_id"],replication_runs=[{"outcome":"supports","independent":True,"run_type":"simulation"},{"outcome":"supports","independent":True,"run_type":"simulation"}],verification_context="physical")
    assert replication["status"]=="REPLICATED"
    kinds=[e["event_type"] for e in engine.get_invention_ledger(iid)["events"]]
    assert "REPLICATION" in kinds; assert "INDEPENDENT_VERIFICATION" not in kinds


def test_direct_prior_art_still_blocks_candidate_acceptance():
    record=_new(); iid=record["investigation_id"]
    analogy=engine.add_analogy(iid,source_subject="Biology",target_subject="Engineering",source_concept="branching",mechanism="distribution",transferable_principle="distributed paths",constraints=[])
    candidate=engine.generate_candidate_hypothesis(iid,analogy_id=analogy["analogy_id"],statement="Branching improves cooling.",rationale="Distributed paths.",assumptions=[],falsification_criteria=["No improvement."],expected_observations=[],target_measurements=["temperature"])
    engine.assess_candidate_prior_art(iid,candidate_id=candidate["candidate_id"],search_queries=["branching cooler"],matches=[{"title":"existing","similarity":"DIRECT"}])
    try: engine.accept_candidate_hypothesis(iid,candidate["candidate_id"])
    except engine.DiscoveryEngineError as exc: assert "blocked by direct prior art" in str(exc)
    else: raise AssertionError("direct prior art must block acceptance")


def test_simulation_cannot_masquerade_as_experimental_support():
    record=_new(); iid=record["investigation_id"]
    engine.add_hypothesis(iid,statement="Model remains stable.",rationale="Equations are bounded.",falsification_criteria=["Solver diverges."])
    engine.set_experiment_plan(iid,objective="run model",method=["simulate"],measurements=["stability"],pass_fail_criteria=["bounded"])
    try: engine.record_result(iid,result_type="simulation",summary="bounded",resulting_status="EXPERIMENTALLY_SUPPORTED")
    except engine.DiscoveryEngineError as exc: assert "simulation cannot" in str(exc)
    else: raise AssertionError("simulation must not masquerade as experimental support")


def test_manual_independent_verification_assertion_is_rejected():
    record=_new(); iid=record["investigation_id"]
    engine.add_hypothesis(iid,statement="Effect exists.",rationale="Signal expected.",falsification_criteria=["No signal."])
    engine.set_experiment_plan(iid,objective="measure",method=["measure"],measurements=["signal"],pass_fail_criteria=["above threshold"])
    try: engine.record_result(iid,result_type="experiment",summary="caller assertion",resulting_status="INDEPENDENTLY_VERIFIED")
    except engine.DiscoveryEngineError as exc: assert "replication manager" in str(exc)
    else: raise AssertionError("verification must come through replication manager")


def test_invalid_knowledge_layer_fails_truthfully():
    try: engine.create_investigation(title="Bad layer",question="Is this layer allowed?",knowledge_layer="MAGIC")
    except engine.DiscoveryEngineError as exc: assert "invalid knowledge_layer" in str(exc)
    else: raise AssertionError("invalid knowledge layer must fail")
