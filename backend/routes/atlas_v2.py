"""
ATLAS V2 routes — worldwatch + self-code + adaptation + visual style.

Prefixes:
  /api/worldwatch/*
  /api/self-code/*
  /api/learning/*
  /api/style/*
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import worldwatch as ww
from services import self_code as sc
from services import adaptation as ad

router = APIRouter(tags=["AtlasV2"])


# --- /api/worldwatch ------------------------------------------------------
@router.get("/api/worldwatch/status")
async def worldwatch_status():
    return await ww.status()


@router.post("/api/worldwatch/seed")
async def worldwatch_seed():
    return await ww.seed_feeds()


class WWRunReq(BaseModel):
    max_per_feed: int = Field(3, ge=1, le=10)


@router.post("/api/worldwatch/run")
async def worldwatch_run(req: Optional[WWRunReq] = None):
    n = (req.max_per_feed if req else 3)
    return await ww.run(max_per_feed=n)


@router.get("/api/worldwatch/updates")
async def worldwatch_updates(
    domain: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
):
    items = await ww.list_updates(domain=domain, limit=limit)
    return {"count": len(items), "items": items}


@router.get("/api/worldwatch/feeds")
async def worldwatch_feeds(domain: Optional[str] = None):
    items = await ww.list_feeds(domain=domain)
    return {"count": len(items), "items": items}


# --- /api/self-code -------------------------------------------------------
@router.get("/api/self-code/proposals")
async def selfcode_proposals(
    status: Optional[str] = "pending",
    limit: int = Query(200, ge=1, le=500),
):
    from services import self_improvement as si
    items = await si.list_proposals(status=status, limit=limit)
    # filter to scanner-sourced ones
    items = [d for d in items if d.get("source") == "self-code-scanner"]
    return {"count": len(items), "items": items}


@router.post("/api/self-code/scan")
async def selfcode_scan(root: Optional[str] = None):
    return await sc.scan(root=root)


@router.post("/api/self-code/approve/{improvement_id}")
async def selfcode_approve(improvement_id: str):
    from services import self_improvement as si
    res = await si.decide(improvement_id, status="approved", note="approved via self-code")
    if not res: raise HTTPException(404, "proposal not found")
    return res


@router.post("/api/self-code/reject/{improvement_id}")
async def selfcode_reject(improvement_id: str):
    from services import self_improvement as si
    res = await si.decide(improvement_id, status="rejected", note="rejected via self-code")
    if not res: raise HTTPException(404, "proposal not found")
    return res


# --- /api/learning --------------------------------------------------------
class LearningPatchReq(BaseModel):
    patch: Dict[str, Any]


@router.get("/api/learning/profile")
async def learning_profile():
    return await ad.get_learning_profile()


@router.post("/api/learning/profile")
async def learning_profile_update(req: LearningPatchReq):
    return await ad.update_learning_profile(req.patch or {})


class ConfusionReq(BaseModel):
    topic: str
    weight: int = 1


@router.post("/api/learning/log-confusion")
async def learning_log_confusion(req: ConfusionReq):
    return await ad.log_confusion(req.topic, weight=req.weight)


class SuccessReq(BaseModel):
    lesson_id: str
    pattern: str


@router.post("/api/learning/log-success")
async def learning_log_success(req: SuccessReq):
    return await ad.log_successful_lesson(req.lesson_id, req.pattern)


# --- /api/style -----------------------------------------------------------
@router.get("/api/style/preferences")
async def style_preferences():
    return await ad.get_visual_style()


@router.post("/api/style/preferences")
async def style_preferences_update(req: LearningPatchReq):
    return await ad.update_visual_style(req.patch or {})


class StyleNoteReq(BaseModel):
    note: str


@router.post("/api/style/note")
async def style_note(req: StyleNoteReq):
    return await ad.add_style_note(req.note)


class StyleWarningReq(BaseModel):
    kind: str   # 'too_plain' | 'too_messy'


@router.post("/api/style/warning")
async def style_warning(req: StyleWarningReq):
    try:
        return await ad.increment_warning(req.kind)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


# --- /api/themes (read-only theme tokens served from disk) ----------------
@router.get("/api/themes/list")
async def themes_list():
    import json
    from pathlib import Path
    base = Path("/app/themes")
    out = []
    if base.exists():
        for f in sorted(base.glob("*.json")):
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
                out.append({
                    "id": f.stem,
                    "filename": f.name,
                    "name": doc.get("name", f.stem),
                    "kind": doc.get("kind", "theme"),
                    "version": doc.get("version", "1.0.0"),
                })
            except Exception:
                pass
    return {"count": len(out), "items": out}


@router.get("/api/themes/{theme_id}")
async def themes_get(theme_id: str):
    import json
    from pathlib import Path
    f = Path(f"/app/themes/{theme_id}.json")
    if not f.exists():
        raise HTTPException(404, "theme not found")
    return json.loads(f.read_text(encoding="utf-8"))
