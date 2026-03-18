from fastapi import APIRouter

router = APIRouter(prefix="/chameleon", tags=["chameleon"])


@router.get("/status")
def chameleon_status():
    return {"status": "stub", "module": "doctrine.chameleon_api"}
