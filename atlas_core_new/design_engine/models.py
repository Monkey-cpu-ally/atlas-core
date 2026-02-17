from pydantic import BaseModel
from typing import List, Optional


class ProjectInput(BaseModel):
    name: str
    description: str


class ConstraintModel(BaseModel):
    name: Optional[str] = None
    scale: Optional[str] = None
    energy: Optional[str] = None
    materials: Optional[List[str]] = None
    fabrication: Optional[List[str]] = None
    physics: Optional[str] = None


class IterationResult(BaseModel):
    variant_name: str
    performance_score: float
    notes: str
