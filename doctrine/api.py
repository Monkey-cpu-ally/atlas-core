from fastapi import APIRouter

router = APIRouter(prefix="/doctrine", tags=["doctrine"])


@router.get("/status")
def doctrine_status():
    return {"status": "stub", "module": "doctrine.api"}
