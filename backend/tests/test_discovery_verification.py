from services import discovery_verification as verification

def test_experiment_design_is_not_result():
    plan=verification.design_experiment(hypothesis="A improves B",independent_variables=["A"],dependent_variables=["B"],controls=["baseline"],procedure=["measure baseline","apply A","measure B"],pass_fail_criteria=["B improves >= 5%"])
    assert plan["status"]=="TEST_DESIGNED"; assert "not a result" in plan["claim_rule"]

def test_weak_evidence_remains_insufficient():
    result=verification.evaluate_evidence(evidence=[{"source_type":"unknown"}])
    assert result["disposition"]=="INSUFFICIENT_EVIDENCE"

def test_conflict_overrides_strong_evidence_routing():
    evidence=[{"source_type":"peer_reviewed","citation":"A","direct_support":True},{"source_type":"government","citation":"B","direct_support":True}]
    result=verification.evaluate_evidence(evidence=evidence,conflicts=[{"claim":"opposing result"}])
    assert result["disposition"]=="CONFLICT_REVIEW_REQUIRED"

def test_replication_without_independent_run_is_not_independently_verified():
    result=verification.evaluate_replication(original_result={"value":1},replication_runs=[{"outcome":"supports","independent":False},{"outcome":"supports","independent":False}],required_successes=2)
    assert result["status"]=="REPLICATED"; assert result["independent_support_count"]==0

def test_independent_replication_can_reach_verified_state():
    result=verification.evaluate_replication(original_result={"value":1},replication_runs=[{"outcome":"supports","independent":False},{"outcome":"supports","independent":True}],required_successes=2)
    assert result["status"]=="INDEPENDENTLY_VERIFIED"
