from fastapi import APIRouter

router = APIRouter(prefix="/pre-reality", tags=["pre-reality"])


@router.get("/status")
def pre_reality_status():
    return {"status": "stub", "module": "pre_reality_engine.api"}
