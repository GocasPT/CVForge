from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from backend.models import Project


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Project title")
    description: str = Field(..., min_length=10, description="Project description")
    technologies: List[str] = Field(default_factory=list, description="List of technologies used")
    achievements: List[str] = Field(default_factory=list, description="List of achievements")
    duration: str = Field(..., min_length=1, max_length=255, description="Project duration")
    role: Optional[str] = Field(None, max_length=255, description="Your role in the project")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    technologies: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    duration: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = Field(None, max_length=255)


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_model(cls, project: "Project") -> "ProjectResponse":
        return cls.model_validate(project)


class ProjectListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    projects: List[ProjectResponse]
    
    model_config = ConfigDict(from_attributes=True)