"""Targeted research entry point for the Knowledge Bookshelf.

This deliberately reuses the existing ingestion, Memory Bank, graph and lesson
services. It does not run global WorldWatch discovery, so a Bookshelf action
cannot silently research unrelated topics.
"""
from typing import Any, Dict, Optional
from uuid import uuid4
from services import knowledge_ingestion as ki
from services import memory_bank as mb
from services import lesson_generator as lg
from services import research_orchestrator as ro

async def investigate_target(*,subject:str,title:str,resource_id:Optional[str]=None,source_url:Optional[str]=None,context:Optional[str]=None,generate_lesson:bool=True,mode:str="lego") -> Dict[str,Any]:
    if not source_url:
        # Without a resolvable source, record an explicit mission instead of
        # fabricating web evidence. A later discovery connector can satisfy it.
        mission={"id":uuid4().hex,"kind":"bookshelf_targeted_research","title":f"Research more: {title}"[:280],"target":title,"subject":subject,"resource_id":resource_id,"context":context or "","status":"open","evidence":ro.make_evidence(source="knowledge_bookshelf",confidence=0.5,evidence_refs=[{"kind":"resource","id":resource_id or "unassigned","title":title}],verification_status="manual"),"created_at":ro._utc()}
        await ro._missions().insert_one(mission)
        return {"status":"mission_created","mission_id":mission["id"],"subject":subject,"title":title,"reason":"selected resource has no source URL; no evidence was fabricated"}

    item=await ro.enqueue_item(source_type="bookshelf",url=source_url,title=title,domain=subject,agent="minerva",payload={"resource_id":resource_id,"context":context or "","origin":"knowledge_bookshelf"},confidence=0.6)
    await ro._set_state(item["id"],"queued",by="bookshelf_targeted_research")
    await ro._set_state(item["id"],"investigating",by="bookshelf_targeted_research")
    result=await ki.ingest_url(source_url,extra_tags=["bookshelf_targeted_research",f"domain:{subject}",f"resource:{resource_id or 'unassigned'}"])
    rec=result.get("record") or {};kb_id=rec.get("id");mb_id=result.get("memory_bank_id");concepts=rec.get("concepts") or [];conf=float(rec.get("confidence_score") or 0.0)
    await ro._set_state(item["id"],"analyzed",by="bookshelf_targeted_research",extra={"knowledge_id":kb_id,"memory_bank_id":mb_id})
    verification="automated" if conf>=0.4 and concepts else "weak"
    evidence=ro.make_evidence(source="bookshelf",confidence=conf,evidence_refs=[{"kind":"source","url":source_url},{"kind":"knowledge","id":kb_id},{"kind":"concepts","count":len(concepts)}],verification_status=verification)
    await ro._queue().update_one({"id":item["id"]},{"$set":{"evidence":evidence}})
    await ro._set_state(item["id"],"verified",by="bookshelf_targeted_research");await ro._set_state(item["id"],"stored",by="bookshelf_targeted_research")
    if kb_id:
        try: await mb.add_triple(from_node=f"resource:{resource_id or item['id'][:8]}",to_node=kb_id,relation="researched_more",source_id=item["id"],weight=1.0)
        except Exception: pass
    await ro._set_state(item["id"],"linked",by="bookshelf_targeted_research")
    lesson_id=None
    if generate_lesson and kb_id and concepts:
        lesson=await lg.generate_lesson(knowledge_id=kb_id,source_url=source_url,title=rec.get("title") or title,concepts=concepts,agent="minerva",mode=mode);lesson_id=lesson.get("id")
        if lesson_id:
            await ro._queue().update_one({"id":item["id"]},{"$push":{"lesson_ids":lesson_id}});await ro._set_state(item["id"],"lesson_generated",by="bookshelf_targeted_research")
    return {"status":"done","queue_id":item["id"],"knowledge_id":kb_id,"memory_bank_id":mb_id,"lesson_id":lesson_id,"verification":verification,"confidence":conf,"concepts_count":len(concepts),"subject":subject,"title":title}
