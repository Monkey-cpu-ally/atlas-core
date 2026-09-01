from services import discovery_ideation as ideation


def test_cross_disciplinary_analogy_stays_unvalidated():
    analogy=ideation.build_analogy(source_subject="Biology",target_subject="Robotics",source_mechanism="compliant joints distribute transient loads",target_problem="robot gripper impact tolerance",shared_principle="distributed compliance",assumptions=["load scales are comparable"],failure_modes=["compliance reduces positioning accuracy"])
    assert analogy["status"]=="UNVALIDATED_ANALOGY"
    assert "not evidence" in analogy["claim_rule"]


def test_same_subject_is_not_cross_disciplinary():
    try: ideation.build_analogy(source_subject="Physics",target_subject="physics",source_mechanism="x",target_problem="y",shared_principle="z",assumptions=[],failure_modes=["bad transfer"])
    except ideation.DiscoveryIdeationError as exc: assert "different" in str(exc)
    else: raise AssertionError("same-subject analogy must fail")


def test_candidate_hypothesis_requires_falsification_and_remains_candidate():
    analogy=ideation.build_analogy(source_subject="Botany",target_subject="Architecture",source_mechanism="branching structures distribute loads",target_problem="lightweight roof support",shared_principle="hierarchical branching",assumptions=["material behavior is represented separately"],failure_modes=["joint concentration dominates"])
    candidate=ideation.hypothesis_from_analogy(analogy=analogy,measurable_effect="reduce structural mass at equal design load",comparison="a non-branching baseline",falsification_criteria=["mass reduction is <= 0% at equal safety factor"])
    assert candidate["status"]=="CANDIDATE_ONLY"
    assert candidate["required_next_steps"]==["prior_art_search","evidence_review","experiment_design"]
    assert candidate["source_analogy_id"]==analogy["analogy_id"]
