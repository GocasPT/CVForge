from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class ProjectCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    description: str
    technologies: List[str]
    achievements: List[str]
    duration: str
    role: Optional[str] = None


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    duration: Optional[str] = None
    role: Optional[str] = None


class ProjectResponse(ProjectCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total: int
    offset: int
    limit: int
    projects: List[ProjectResponse]
