from fastapi import APIRouter

router = APIRouter(prefix="/simulator", tags=["simulator"])


@router.get("/status")
def simulator_status():
    return {"status": "stub", "module": "umojaforge.simulator_api"}
