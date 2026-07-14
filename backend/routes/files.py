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

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "atlas_core")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# File storage directory. Production can set ATLAS_UPLOAD_DIR=/app/uploads.
# Local development and CI default to a writable repository-local directory.
_default_upload_dir = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR = Path(os.environ.get("ATLAS_UPLOAD_DIR", str(_default_upload_dir))).expanduser()
try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    UPLOAD_DIR = Path("/tmp/atlas-uploads")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# File size limit: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and get AI categorization suggestion."""
    try:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")

        file_id = f"file_{uuid4().hex[:12]}"
        file_extension = os.path.splitext(file.filename)[1]
        stored_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / stored_filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ai_suggestion = await categorize_file_with_ai(
            filename=file.filename,
            file_type=file.content_type or "application/octet-stream",
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
            user_confirmed=False,
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
                "description": ai_suggestion["description"],
            },
            message="File uploaded successfully. AI has suggested categorization.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}") from exc


@router.get("/list", response_model=List[FileMetadata])
async def list_files(
    ai_persona: str = Query(None, description="Filter by AI persona"),
    section: str = Query(None, description="Filter by section"),
    limit: int = Query(100, description="Maximum number of files to return"),
):
    query = {}
    if ai_persona:
        query["ai_persona"] = ai_persona
    if section:
        query["section"] = section
    return await db.files.find(query, {"_id": 0}).limit(limit).to_list(limit)


@router.get("/sections")
async def available_sections():
    return {"sections": get_available_sections()}


@router.get("/{file_id}", response_model=FileMetadata)
async def get_file(file_id: str):
    record = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    return record


@router.get("/{file_id}/download")
async def download_file(file_id: str):
    record = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(record["file_path"], filename=record["filename"])


@router.patch("/{file_id}/category", response_model=FileMetadata)
async def update_file_category(file_id: str, update: FileCategoryUpdate):
    changes = update.dict(exclude_unset=True)
    changes["user_confirmed"] = True
    result = await db.files.find_one_and_update(
        {"id": file_id},
        {"$set": changes},
        return_document=True,
        projection={"_id": 0},
    )
    if not result:
        raise HTTPException(status_code=404, detail="File not found")
    return result


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    record = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    path = Path(record["file_path"])
    if path.exists():
        path.unlink()
    await db.files.delete_one({"id": file_id})
    return {"success": True, "file_id": file_id}
