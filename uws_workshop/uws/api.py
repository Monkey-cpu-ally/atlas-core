from fastapi import APIRouter

router = APIRouter(prefix="/uws", tags=["uws"])


@router.get("/status")
def uws_status():
    return {"status": "stub", "module": "uws_workshop.uws.api"}
