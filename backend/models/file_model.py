"""
File Upload Model
Stores metadata for uploaded files with AI categorization
"""
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field

class FileMetadata(BaseModel):
    """File metadata model"""
    id: str = Field(..., description="Unique file ID")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Server file path")
    file_type: str = Field(..., description="File MIME type")
    file_size: int = Field(..., description="File size in bytes")
    ai_persona: str = Field(..., description="Assigned AI (ajani/minerva/hermes/trinity)")
    section: str = Field(..., description="Category section (projects/lab/subjects/blueprints/archives)")
    tags: List[str] = Field(default_factory=list, description="Auto-generated tags")
    description: Optional[str] = Field(None, description="AI-generated description")
    uploaded_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    user_confirmed: bool = Field(default=False, description="User confirmed AI categorization")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "file_123abc",
                "filename": "solar_energy_research.pdf",
                "file_path": "/app/uploads/file_123abc.pdf",
                "file_type": "application/pdf",
                "file_size": 2048576,
                "ai_persona": "ajani",
                "section": "projects",
                "tags": ["energy", "solar", "research"],
                "description": "Research document on solar energy systems",
                "uploaded_at": "2026-01-01T12:00:00Z",
                "user_confirmed": True
            }
        }

class FileUploadResponse(BaseModel):
    """Response after file upload and AI categorization"""
    success: bool
    file_id: str
    filename: str
    ai_suggestion: dict  # Contains ai_persona, section, tags, description
    message: str

class FileCategoryUpdate(BaseModel):
    """Request to update file categorization"""
    file_id: str
    ai_persona: str
    section: str
    user_confirmed: bool = True
