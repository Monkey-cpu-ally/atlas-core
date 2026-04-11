"""
File Upload and Management Routes
Handles file uploads, AI categorization, and file management
"""
import os
import shutil
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

# File storage directory
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# File size limit: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file and get AI categorization suggestion
    """
    try:
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File too large. Maximum size is 50MB")
        
        # Generate unique file ID
        file_id = f"file_{uuid4().hex[:12]}"
        file_extension = os.path.splitext(file.filename)[1]
        stored_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, stored_filename)
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get AI categorization suggestion
        ai_suggestion = await categorize_file_with_ai(
            filename=file.filename,
            file_type=file.content_type or "application/octet-stream"
        )
        
        # Store metadata in MongoDB
        file_metadata = FileMetadata(
            id=file_id,
            filename=file.filename,
            file_path=file_path,
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list", response_model=List[FileMetadata])
async def list_files(
    ai_persona: str = Query(None, description="Filter by AI persona"),
    section: str = Query(None, description="Filter by section"),
    limit: int = Query(100, description="Maximum number of files to return")
):
    """
    List uploaded files with optional filtering
    """
    query = {}
    if ai_persona:
        query["ai_persona"] = ai_persona
    if section:
        query["section"] = section
    
    files = await db.files.find(query, {"_id": 0}).limit(limit).to_list(limit)
    return files


@router.put("/categorize")
async def update_categorization(update: FileCategoryUpdate):
    """
    Update file categorization (user confirmation or manual change)
    """
    # Verify file exists
    file_doc = await db.files.find_one({"id": update.file_id}, {"_id": 0})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Verify section is valid for AI persona
    valid_sections = get_available_sections(update.ai_persona)
    if update.section not in valid_sections:
        raise HTTPException(
            status_code=400,
            detail=f"Section '{update.section}' not valid for AI persona '{update.ai_persona}'. Valid sections: {valid_sections}"
        )
    
    # Update categorization
    await db.files.update_one(
        {"id": update.file_id},
        {"$set": {
            "ai_persona": update.ai_persona,
            "section": update.section,
            "user_confirmed": update.user_confirmed
        }}
    )
    
    return {"success": True, "message": "Categorization updated"}


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """
    Delete a file and its metadata
    """
    # Get file metadata
    file_doc = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete physical file
    try:
        if os.path.exists(file_doc["file_path"]):
            os.remove(file_doc["file_path"])
    except Exception as e:
        print(f"Error deleting file: {e}")
    
    # Delete metadata from database
    await db.files.delete_one({"id": file_id})
    
    return {"success": True, "message": "File deleted"}


@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """
    Download a file
    """
    file_doc = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not os.path.exists(file_doc["file_path"]):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_doc["file_path"],
        filename=file_doc["filename"],
        media_type=file_doc["file_type"]
    )


@router.get("/stats")
async def get_file_stats():
    """
    Get file upload statistics
    """
    total_files = await db.files.count_documents({})
    
    # Count by AI persona
    by_persona = {}
    for persona in ["ajani", "minerva", "hermes", "trinity"]:
        count = await db.files.count_documents({"ai_persona": persona})
        by_persona[persona] = count
    
    # Count by section
    by_section = {}
    for section in ["projects", "lab", "subjects", "blueprints", "archives"]:
        count = await db.files.count_documents({"section": section})
        by_section[section] = count
    
    return {
        "total_files": total_files,
        "by_ai_persona": by_persona,
        "by_section": by_section
    }
