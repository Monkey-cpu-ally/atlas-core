import asyncio
import json
from unittest.mock import AsyncMock, patch

from creative_intelligence.craft_rubrics import STORY
from creative_intelligence.executor_registry import ExecutionRequest
from creative_intelligence.story_production import StoryBrief, StoryProductionService
from backend.services.creative_critique_executor import execute_critique
from backend.services.creative_revision_executor import execute_revision
from backend.services.creative_master_executor import REQUIRED_GATES, execute_master


def reference_context():
    return {
        "query":"visual storytelling",
        "project_identity":"Original machine-world family drama",
        "project_constraints":["no gore","functional machinery"],
        "reference_ids":["creator:test"],
        "principles":["strong silhouettes","visual clarity"],
        "study_targets":["staging"],
        "limitations":["do not imitate distinctive expression"],
        "provenance":["curated creator profile"],
        "contract":{
            "principle_only":True,
            "project_identity_overrides_reference_influence":True,
            "project_constraints_preserved":True,
            "constraints_are_not_inspiration":True,
        },
    }


def critic_response(score=95, revisions=None):
    return json.dumps({
        "scores":{dimension.name:score for dimension in STORY.dimensions},
        "findings":["Project identity and constraints remain intact."],
        "revision_requests":list(revisions or []),
        "reference_boundary_check":{
            "passed":True,
            "project_alignment":True,
            "constraints_respected":True,
            "anti_imitation":True,
            "findings":["Only transferable principles are present."],
        },
    })


async def run_chain():
    context=reference_context()
    seen={}
    async def generator(spec):
        seen["create_context"]=spec["reference_context"]
        return "Draft: a family repairs a failing machine-city together."
    service=StoryProductionService(generator)
    brief=StoryBrief.from_mapping({
        "premise":"A family must save their living machine-city.",
        "audience":"adult",
        "medium":"short story",
        "tone":"tense and hopeful",
        "constraints":["no gore","functional machinery"],
        "reference_context":context,
    })
    created=await service.create(brief)

    first_reviews=[{"text":critic_response(95,["Clarify the final repair choice."])} for _ in range(3)]
    with patch("backend.services.creative_critique_executor.send",new=AsyncMock(side_effect=first_reviews)):
        first=await execute_critique(ExecutionRequest("job","project","critique",created["artifact_id"],{"artifact":created["text"],"reference_context":context}))

    with patch("backend.services.creative_revision_executor.send",new=AsyncMock(return_value={"text":"Revised: the family chooses a risky manual repair and saves the machine-city without violence."})) as revision_send:
        revised=await execute_revision(ExecutionRequest("job","project","revision",created["artifact_id"],{"artifact":created["text"],"revision_plan":first.output["revision_plan"],"reference_context":context}))
        revision_prompt=revision_send.await_args.args[2]

    final_reviews=[{"text":critic_response()} for _ in range(3)]
    with patch("backend.services.creative_critique_executor.send",new=AsyncMock(side_effect=final_reviews)):
        final=await execute_critique(ExecutionRequest("job","project","critique",revised.artifact_id,{"artifact":revised.output["text"],"reference_context":context}))

    mastered=await execute_master(ExecutionRequest("job","project","master",revised.artifact_id,{
        "artifact":revised.output["text"],
        "reference_context":context,
        "critic_council":final.output,
        "quality_evidence":{gate:{"passed":True} for gate in REQUIRED_GATES},
    }))
    return context,seen,first,revised,revision_prompt,final,mastered


def test_full_production_chain_preserves_authority_provenance_and_boundaries():
    context,seen,first,revised,revision_prompt,final,mastered=asyncio.run(run_chain())
    assert seen["create_context"]["project_identity"]==context["project_identity"]
    assert tuple(seen["create_context"]["project_constraints"])==tuple(context["project_constraints"])
    assert tuple(seen["create_context"]["provenance"])==tuple(context["provenance"])
    assert first.output["reference_boundaries_verified"] is True
    assert revised.output["reference_context_preserved"] is True
    revision_payload=json.loads(revision_prompt)
    assert revision_payload["reference_context"]["project_identity"]==context["project_identity"]
    assert tuple(revision_payload["reference_context"]["project_constraints"])==tuple(context["project_constraints"])
    assert tuple(revision_payload["reference_context"]["provenance"])==tuple(context["provenance"])
    assert final.output["approved"] is True
    assert len(final.output["reference_boundary_checks"])==3
    assert all(check["anti_imitation"] for check in final.output["reference_boundary_checks"])
    assert mastered.output["approved"] is True
    assert mastered.output["reference_boundaries_verified"] is True
    assert "originality" in mastered.output["passed_gates"]
