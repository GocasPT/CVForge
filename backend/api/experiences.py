from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, validator

from backend.config import SessionLocal
from backend.models import Experience

router = APIRouter()

@router.get("/")
def get_experiences(
    limit: int = Query(10, ge=1, le=100),
    offset: int = 0,
    search: str | None = None
):
    session = SessionLocal()
    try:
        query = session.query(Experience)

        if search:
            query = query.filter(
                (Experience.position.ilike(f"%{search}%")) |
                (Experience.company.ilike(f"%{search}%")) |
                (Experience.description.ilike(f"%{search}%"))
            )

        experiences = query.order_by(Experience.start_date.desc()).offset(offset).limit(limit).all()
    finally:
        session.close()

    return {"experiences": experiences, "offset": offset, "limit": limit}

@router.get("/{id}")
def get_experience(id: int):
    session = SessionLocal()
    try:
        query = session.query(Experience)

        experience = query.get(id)
        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")

    finally:
        session.close()

    return experience

class ExperienceCreate(BaseModel):
    position: str
    company: str
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    achievements: Optional[List[str]] = None

    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "position": "Backend Engineer",
                "company": "TechCorp",
                "location": "Remote",
                "start_date": "2022-01-01",
                "end_date": "2023-12-31",
                "description": "Developed scalable APIs",
                "technologies": ["Python", "FastAPI", "PostgreSQL"],
                "achievements": ["Increased API performance by 40%"]
            }
        }

@router.post("/")
def create_experience(data: ExperienceCreate):
    session = SessionLocal()
    new_experience = Experience(**data.model_dump())
    if new_experience is None:
        raise HTTPException(status_code=500, detail="JSON in wrong format")

    try:
        session.add(new_experience)
        session.commit()

        experience_dict = new_experience.as_dict()

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    finally:
        session.close()

    return {"status": "created", "experience": experience_dict}

@router.put("/{id}")
def update_experience(id: int, data: dict):
    session = SessionLocal()
    try:
        experience = session.query(Experience).get(id)
        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")

        for key, value in data.items():
            if hasattr(experience, key):
                setattr(experience, key, value)

        session.commit()
        updated_experience = experience.as_dict()

    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    finally:
        session.close()

    return {"status": "updated", "experience": updated_experience}

@router.delete("/{id}")
def delete_experience(id: int):
    session = SessionLocal()
    try:
        experience = session.query(Experience).get(id)
        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")

        session.delete(experience)
        session.commit()

    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    finally:
        session.close()

    return {"status": "deleted"}