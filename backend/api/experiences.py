from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from backend.config import get_db
from backend.models import Experience

router = APIRouter()

@router.get("")
def get_experiences(
    limit: int = Query(10, ge=1, le=100),
    offset: int = 0,
    search: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Experience)

    if search:
        query = query.filter(
            (Experience.position.ilike(f"%{search}%")) |
            (Experience.company.ilike(f"%{search}%")) |
            (Experience.description.ilike(f"%{search}%"))
        )

    experiences = query.order_by(Experience.start_date.desc()).offset(offset).limit(limit).all()

    return { "offset": offset, "limit": limit, "experiences": experiences }

@router.get("/{id}")
def get_experience(
    id: int,
    db: Session = Depends(get_db)
):
    query = db.query(Experience)

    experience = query.get(id)
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")

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

@router.post("")
def create_experience(
    data: ExperienceCreate,
    db: Session = Depends(get_db)
):
    new_experience = Experience(**data.model_dump())
    if new_experience is None:
        raise HTTPException(status_code=500, detail="JSON in wrong format")

    try:
        db.add(new_experience)
        db.commit()

        experience_dict = new_experience.as_dict()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")


    return {"status": "created", "experience": experience_dict}

@router.put("/{id}")
def update_experience(
    id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    try:
        experience = db.query(Experience).get(id)
        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")

        for key, value in data.items():
            if hasattr(experience, key):
                setattr(experience, key, value)

        db.commit()
        updated_experience = experience.as_dict()

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    return {"status": "updated", "experience": updated_experience}

@router.delete("/{id}")
def delete_experience(
    id: int,
    db: Session = Depends(get_db)
):
    try:
        experience = db.query(Experience).get(id)
        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")

        db.delete(experience)
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    return {"status": "deleted"}