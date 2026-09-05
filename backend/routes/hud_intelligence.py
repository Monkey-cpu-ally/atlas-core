"""Versioned, feature-gated HTTP surface for HUD Intelligence V1."""
from fastapi import APIRouter, HTTPException

from models.hud_intelligence_models import HudIntelligenceRequest, HudIntelligenceResponse
import services.hud_intelligence as service

router = APIRouter(prefix="/api/v1/hud/intelligence", tags=["HUD Intelligence V1"])


@router.post("", response_model=HudIntelligenceResponse)
async def run_intelligence(req: HudIntelligenceRequest):
    if not service.feature_enabled():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "hud_intelligence_v1_disabled",
                "message": "HUD Intelligence V1 is disabled by feature flag.",
                "retryable": False,
            },
        )
    try:
        return await service.execute(req)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "hud_intelligence_unavailable",
                "message": "HUD Intelligence V1 is temporarily unavailable.",
                "retryable": True,
            },
        ) from exc

