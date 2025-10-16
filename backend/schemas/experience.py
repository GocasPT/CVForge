from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime


class ExperienceCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    position: str
    company: str
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: List[str]
    achievements: List[str]

class ExperienceUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    position: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    achievements: Optional[List[str]] = None

class ExperienceResponse(ExperienceCreate):
    id: int
    created_at: datetime
    updated_at: datetime

class ExperienceListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total: int
    offset: int
    limit: int
    experiences: List[ExperienceResponse]