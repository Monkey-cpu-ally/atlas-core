"""NIR REST API — Phase D4.

Mounted at `/api/nir/*`.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from models.nir_models import LibraryEntry, NIRSource, NIRSpectrum
from services import nir as nir_svc

router = APIRouter(prefix="/api/nir", tags=["NIR Scanner"])


class ScanReq(BaseModel):
    label: Optional[str] = None
    source: NIRSource = NIRSource.LAB_INSTRUMENT
    device_id: Optional[str] = None
    wavelengths_nm: List[float]
    intensities: List[float]
    integration_ms: Optional[float] = None
    temperature_c: Optional[float] = None
    tags: List[str] = Field(default_factory=list)


@router.post("/scan")
async def scan(req: ScanReq):
    spec = NIRSpectrum(**req.model_dump())
    res = await nir_svc.ingest_and_analyse(spec)
    if not res.get("ok"):
        raise HTTPException(400, {"errors": res.get("errors", [])})
    return res


class SyntheticReq(BaseModel):
    material_name: str
    label: Optional[str] = None


@router.post("/scan/synthetic")
async def scan_synthetic(req: SyntheticReq):
    """Generate a synthetic NIR scan for one of the seed library
    materials and run it through the full analysis. Used for demos /
    tests when no real instrument is connected."""
    try:
        spec = nir_svc.synthesize_spectrum(req.material_name)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if req.label:
        spec.label = req.label
    return await nir_svc.ingest_and_analyse(spec)


@router.get("/scans")
async def scans(limit: int = Query(50, ge=1, le=200)):
    items = await nir_svc.list_scans(limit=limit)
    return {"count": len(items), "items": items}


@router.get("/results")
async def results(limit: int = Query(50, ge=1, le=200)):
    items = await nir_svc.list_results(limit=limit)
    return {"count": len(items), "items": items}


@router.get("/results/{spectrum_id}")
async def result(spectrum_id: str):
    res = await nir_svc.get_result_for(spectrum_id)
    if not res:
        raise HTTPException(404, "result not found")
    return res


@router.get("/library")
async def library():
    items = await nir_svc.list_library()
    return {"count": len(items), "items": items}


class LibraryAddReq(BaseModel):
    name: str
    category: str
    characteristic_peaks_nm: List[float]
    fingerprint_intensities: Optional[List[float]] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


@router.post("/library")
async def library_add(req: LibraryAddReq):
    entry = LibraryEntry(**req.model_dump())
    return await nir_svc.add_library_entry(entry)


@router.post("/library/seed")
async def library_seed():
    n = await nir_svc.seed_library_if_needed()
    items = await nir_svc.list_library()
    return {"inserted": n, "total": len(items)}
