from fastapi import APIRouter, HTTPException
from atlas_core_new.hermes_reality.schema import from_dict
from atlas_core_new.hermes_reality.validator import validate_and_simulate

router = APIRouter(prefix="/api/reality", tags=["reality"])

@router.post("/validate")
def validate(payload: dict):
    try:
        spec = from_dict(payload)
        return validate_and_simulate(spec)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
