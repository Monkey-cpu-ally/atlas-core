"""
File Upload and Management Routes
Handles file uploads, AI categorization, and file management.
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient

from models.file_model import FileCategoryUpdate, FileMetadata, FileUploadResponse
from services.ai_categorizer import categorize_file_with_ai, get_available_sections

router = APIRouter(prefix="/api/files", tags=["Files"])

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "atlas_core")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


def _resolve_upload_dir() -> str:
    """Return a writable upload directory without assuming `/app` exists."""
    configured = (os.environ.get("UPLOAD_DIR") or "").strip()
    if configured:
        path = Path(configured).expanduser()
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RuntimeError(
                f"Configured UPLOAD_DIR is not writable: {path}: {exc}"
            ) from exc
        if not os.access(path, os.W_OK | os.X_OK):
            raise RuntimeError(f"Configured UPLOAD_DIR is not writable: {path}")
        return str(path)

    errors = []
    for path in (Path("/app/uploads"), Path(tempfile.gettempdir()) / "atlas-uploads"):
        try:
            path.mkdir(parents=True, exist_ok=True)
            if os.access(path, os.W_OK | os.X_OK):
                return str(path)
            errors.append(f"{path}: not writable")
        except OSError as exc:
            errors.append(f"{path}: {exc}")

    raise RuntimeError("No writable upload directory available: " + "; ".join(errors))


UPLOAD_DIR = _resolve_upload_dir()
MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and get an AI categorization suggestion."""
    file_path = None
    file_id = None
    metadata_inserted = False
    try:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 50MB",
            )

        original_filename = file.filename or "upload.bin"
        file_id = f"file_{uuid4().hex[:12]}"
        file_extension = os.path.splitext(original_filename)[1]
        stored_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, stored_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ai_suggestion = await categorize_file_with_ai(
            filename=original_filename,
            file_type=file.content_type or "application/octet-stream",
        )

        file_metadata = FileMetadata(
            id=file_id,
            filename=original_filename,
            file_path=file_path,
            file_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            ai_persona=ai_suggestion["ai_persona"],
            section=ai_suggestion["section"],
            tags=ai_suggestion["tags"],
            description=ai_suggestion["description"],
            user_confirmed=False,
        )

        await db.files.insert_one(file_metadata.model_dump())
        metadata_inserted = True

        return FileUploadResponse(
            success=True,
            file_id=file_id,
            filename=original_filename,
            ai_suggestion={
                "ai_persona": ai_suggestion["ai_persona"],
                "section": ai_suggestion["section"],
                "tags": ai_suggestion["tags"],
                "description": ai_suggestion["description"],
            },
            message="File uploaded successfully. AI has suggested categorization.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        if metadata_inserted and file_id:
            try:
                await db.files.delete_one({"id": file_id})
            except Exception:
                pass
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}") from exc
    finally:
        try:
            file.file.close()
        except Exception:
            pass


@router.get("/list", response_model=List[FileMetadata])
async def list_files(
    ai_persona: str = Query(None, description="Filter by AI persona"),
    section: str = Query(None, description="Filter by section"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of files to return"),
):
    """List uploaded files with optional filtering."""
    query = {}
    if ai_persona:
        query["ai_persona"] = ai_persona
    if section:
        query["section"] = section

    return await db.files.find(query, {"_id": 0}).limit(limit).to_list(limit)


@router.put("/categorize")
async def update_categorization(update: FileCategoryUpdate):
    """Update file categorization after user confirmation/manual change."""
    file_doc = await db.files.find_one({"id": update.file_id}, {"_id": 0})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    valid_sections = get_available_sections(update.ai_persona)
    if update.section not in valid_sections:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Section '{update.section}' not valid for AI persona "
                f"'{update.ai_persona}'. Valid sections: {valid_sections}"
            ),
        )

    await db.files.update_one(
        {"id": update.file_id},
        {"$set": {
            "ai_persona": update.ai_persona,
            "section": update.section,
            "user_confirmed": update.user_confirmed,
        }},
    )
    return {"success": True, "message": "Categorization updated"}


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Delete a file and its metadata."""
    file_doc = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        if os.path.exists(file_doc["file_path"]):
            os.remove(file_doc["file_path"])
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"File delete failed: {exc}") from exc

    await db.files.delete_one({"id": file_id})
    return {"success": True, "message": "File deleted"}


@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download a stored file."""
    file_doc = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(file_doc["file_path"]):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=file_doc["file_path"],
        filename=file_doc["filename"],
        media_type=file_doc["file_type"],
    )


@router.get("/stats")
async def get_file_stats():
    """Get file upload statistics."""
    total_files = await db.files.count_documents({})

    by_persona = {}
    for persona in ["ajani", "minerva", "hermes", "trinity"]:
        by_persona[persona] = await db.files.count_documents({"ai_persona": persona})

    by_section = {}
    for section in ["projects", "lab", "subjects", "blueprints", "archives"]:
        by_section[section] = await db.files.count_documents({"section": section})

    return {
        "total_files": total_files,
        "by_ai_persona": by_persona,
        "by_section": by_section,
    }
