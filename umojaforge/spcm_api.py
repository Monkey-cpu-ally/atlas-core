from fastapi import APIRouter

router = APIRouter(prefix="/spcm", tags=["spcm"])


@router.get("/status")
def spcm_status():
    return {"status": "stub", "module": "umojaforge.spcm_api"}
