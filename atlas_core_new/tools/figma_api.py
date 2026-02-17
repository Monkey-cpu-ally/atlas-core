"""
Figma Integration API — REST endpoints for Atlas Core's Figma connection.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from atlas_core_new.tools.figma_service import (
    get_connection_status,
    get_file,
    get_file_images,
    get_file_components,
    get_file_styles,
    extract_colors_from_file,
    get_node_details,
    parse_figma_url,
)

router = APIRouter(prefix="/figma", tags=["figma"])


class FigmaFileRequest(BaseModel):
    file_key: Optional[str] = None
    url: Optional[str] = None


class FigmaImageRequest(BaseModel):
    file_key: str
    node_ids: List[str]
    format: str = "png"
    scale: float = 2


class FigmaNodeRequest(BaseModel):
    file_key: str
    node_ids: List[str]


@router.get("/status")
def figma_status():
    return get_connection_status()


@router.post("/file")
def fetch_figma_file(req: FigmaFileRequest):
    file_key = req.file_key
    if not file_key and req.url:
        parsed = parse_figma_url(req.url)
        if "error" in parsed:
            raise HTTPException(status_code=400, detail=parsed["error"])
        file_key = parsed["file_key"]
    if not file_key:
        raise HTTPException(status_code=400, detail="Provide a file_key or a Figma URL")

    result = get_file(file_key)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    result["file_key"] = file_key
    return result


@router.post("/images")
def fetch_figma_images(req: FigmaImageRequest):
    result = get_file_images(req.file_key, req.node_ids, req.format, req.scale)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/components/{file_key}")
def fetch_figma_components(file_key: str):
    result = get_file_components(file_key)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/styles/{file_key}")
def fetch_figma_styles(file_key: str):
    result = get_file_styles(file_key)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/colors/{file_key}")
def fetch_figma_colors(file_key: str):
    result = extract_colors_from_file(file_key)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/nodes")
def fetch_figma_nodes(req: FigmaNodeRequest):
    result = get_node_details(req.file_key, req.node_ids)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/parse-url")
def parse_url(body: dict):
    url = body.get("url", "")
    if not url:
        raise HTTPException(status_code=400, detail="Provide a Figma URL")
    result = parse_figma_url(url)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
