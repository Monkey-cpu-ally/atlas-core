"""
Knowledge Core API Routes
Access to ATLAS Internal 22-Subject Education System
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from services.knowledge_core import get_knowledge_core

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])

# Get the shared knowledge core
knowledge_core = get_knowledge_core()


class TeachRequest(BaseModel):
    subject: str
    topic: str
    persona: Optional[str] = "all"  # ajani, minerva, hermes, or all


class TeachResponse(BaseModel):
    subject: str
    topic: str
    teaching: dict  # Contains ajani, minerva, hermes perspectives
    video_help: List[str]
    projects: List[str]


@router.get("/subjects")
async def list_subjects():
    """
    Get list of all 22 subjects in ATLAS Knowledge Core
    """
    subjects = knowledge_core.list_all_subjects()
    return {
        "total": len(subjects),
        "subjects": subjects,
        "source": "ATLAS_INTERNAL_KNOWLEDGE_CORE"
    }


@router.get("/subjects/{subject}")
async def get_subject_details(subject: str):
    """
    Get detailed information about a specific subject
    Including books, topics, videos, projects
    """
    details = knowledge_core.get_subject_details(subject)
    
    if not details:
        raise HTTPException(
            status_code=404,
            detail=f"Subject '{subject}' not found in Knowledge Core"
        )
    
    return details


@router.post("/teach", response_model=TeachResponse)
async def teach_topic(req: TeachRequest):
    """Teach a topic from the in-memory KnowledgeCore.

    LEGACY (Phase 0 audit): Predates the LLM-powered pipeline in
    `routes/learning.py::generate_lesson`. New integrations should
    target `POST /api/learning/lessons/{id}` or `POST /api/intake/transcript`,
    both of which persist into the `lessons` MongoDB collection.
    Kept for backwards compatibility with the SUBJECTS tile.
    """
    try:
        teaching_response = knowledge_core.teach(req.subject, req.topic)
        
        # Select perspective based on persona
        teaching_dict = {
            "ajani": teaching_response.ajani,
            "minerva": teaching_response.minerva,
            "hermes": teaching_response.hermes
        }
        
        if req.persona and req.persona != "all":
            persona_key = req.persona.lower()
            if persona_key in teaching_dict:
                teaching_dict = {persona_key: teaching_dict[persona_key]}
        
        return TeachResponse(
            subject=teaching_response.subject,
            topic=teaching_response.topic,
            teaching=teaching_dict,
            video_help=teaching_response.video_help,
            projects=teaching_response.projects
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Teaching error: {str(e)}")


@router.get("/search")
async def search_topics(q: str = Query(..., description="Search query for topics")):
    """
    Search for topics across all subjects
    """
    results = knowledge_core.search_topic(q)
    
    return {
        "query": q,
        "found": len(results),
        "subjects": [
            {
                "subject": result.subject,
                "matching_topics": [
                    topic for topic in result.core_topics 
                    if q.lower() in topic.lower()
                ]
            }
            for result in results
        ]
    }


@router.get("/videos/{subject}")
async def get_video_recommendations(subject: str):
    """
    Get video channel/source recommendations for a subject
    """
    subject_data = knowledge_core.get_subject(subject)
    
    if not subject_data:
        raise HTTPException(
            status_code=404,
            detail=f"Subject '{subject}' not found"
        )
    
    return {
        "subject": subject_data.subject,
        "video_sources": subject_data.video_help_sources,
        "recommended_for": "learning and clarification"
    }


@router.get("/projects/{subject}")
async def get_subject_projects(subject: str):
    """
    Get hands-on project recommendations for a subject
    """
    subject_data = knowledge_core.get_subject(subject)
    
    if not subject_data:
        raise HTTPException(
            status_code=404,
            detail=f"Subject '{subject}' not found"
        )
    
    return {
        "subject": subject_data.subject,
        "projects": subject_data.projects,
        "recommended_for": "hands-on learning"
    }


@router.get("/books/{subject}")
async def get_subject_books(subject: str, level: Optional[str] = None):
    """
    Get book recommendations for a subject
    Levels: beginner, hands_on, university, advanced
    """
    subject_data = knowledge_core.get_subject(subject)
    
    if not subject_data:
        raise HTTPException(
            status_code=404,
            detail=f"Subject '{subject}' not found"
        )
    
    books = {
        "beginner": subject_data.books.beginner,
        "hands_on": subject_data.books.hands_on,
        "university": subject_data.books.university,
        "advanced": subject_data.books.advanced,
    }
    
    if level and level in books:
        return {
            "subject": subject_data.subject,
            "level": level,
            "books": books[level]
        }
    
    return {
        "subject": subject_data.subject,
        "all_levels": books
    }
