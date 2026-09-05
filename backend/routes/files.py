"""
File Upload and Management Routes
Handles file uploads, AI categorization, and file management
"""
import os
import shutil
from pathlib import Path
from uuid import uuid4
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient

from models.file_model import FileMetadata, FileUploadResponse, FileCategoryUpdate
from services.ai_categorizer import categorize_file_with_ai, get_available_sections

router = APIRouter(prefix="/api/files", tags=["Files"])

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "atlas_core")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Portable file storage. Production/container deployments may set ATLAS_UPLOAD_DIR
# explicitly (for example /app/uploads). Local development and CI default to a
# repository-local writable directory instead of assuming /app exists.
_DEFAULT_UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR = Path(os.environ.get("ATLAS_UPLOAD_DIR", str(_DEFAULT_UPLOAD_DIR))).expanduser().resolve()
try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except OSError as exc:
    raise RuntimeError(f"ATLAS upload directory is not writable: {UPLOAD_DIR}: {exc}") from exc

MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and get AI categorization suggestion."""
    file_path = None
    try:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")

        file_id = f"file_{uuid4().hex[:12]}"
        file_extension = os.path.splitext(file.filename or "")[1]
        stored_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / stored_filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ai_suggestion = await categorize_file_with_ai(
            filename=file.filename,
            file_type=file.content_type or "application/octet-stream"
        )
        file_metadata = FileMetadata(
            id=file_id,
            filename=file.filename,
            file_path=str(file_path),
            file_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            ai_persona=ai_suggestion["ai_persona"],
            section=ai_suggestion["section"],
            tags=ai_suggestion["tags"],
            description=ai_suggestion["description"],
            user_confirmed=False
        )
        await db.files.insert_one(file_metadata.dict())
        return FileUploadResponse(
            success=True,
            file_id=file_id,
            filename=file.filename,
            ai_suggestion={
                "ai_persona": ai_suggestion["ai_persona"],
                "section": ai_suggestion["section"],
                "tags": ai_suggestion["tags"],
                "description": ai_suggestion["description"]
            },
            message="File uploaded successfully. AI has suggested categorization."
        )
    except HTTPException:
        raise
    except Exception as e:
        if file_path is not None:
            try:
                file_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list", response_model=List[FileMetadata])
async def list_files(ai_persona: str = Query(None), section: str = Query(None), limit: int = Query(100)):
    query = {}
    if ai_persona:
        query["ai_persona"] = ai_persona
    if section:
        query["section"] = section
    return await db.files.find(query, {"_id": 0}).limit(limit).to_list(limit)


@router.put("/categorize")
async def update_categorization(update: FileCategoryUpdate):
    file_doc = await db.files.find_one({"id": update.file_id}, {"_id": 0})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    valid_sections = get_available_sections(update.ai_persona)
    if update.section not in valid_sections:
        raise HTTPException(status_code=400, detail=f"Section '{update.section}' not valid for AI persona '{update.ai_persona}'. Valid sections: {valid_sections}")
    await db.files.update_one({"id": update.file_id}, {"$set": {"ai_persona": update.ai_persona, "section": update.section, "user_confirmed": update.user_confirmed}})
    return {"success": True, "message": "Categorization updated"}


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    file_doc = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    try:
        path = Path(file_doc["file_path"])
        if path.exists():
            path.unlink()
    except Exception as e:
        print(f"Error deleting file: {e}")
    await db.files.delete_one({"id": file_id})
    return {"success": True, "message": "File deleted"}


@router.get("/download/{file_id}")
async def download_file(file_id: str):
    file_doc = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    path = Path(file_doc["file_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(path=str(path), filename=file_doc["filename"], media_type=file_doc["file_type"])


@router.get("/stats")
async def get_file_stats():
    total_files = await db.files.count_documents({})
    by_persona = {}
    for persona in ["ajani", "minerva", "hermes", "trinity"]:
        by_persona[persona] = await db.files.count_documents({"ai_persona": persona})
    by_section = {}
    for section in ["projects", "lab", "subjects", "blueprints", "archives"]:
        by_section[section] = await db.files.count_documents({"section": section})
    return {"total_files": total_files, "by_ai_persona": by_persona, "by_section": by_section}
