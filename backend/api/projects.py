from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.config import get_db
from backend.models import Project

router = APIRouter()

@router.get("")
def get_projects(
    limit: int = Query(10, ge=1, le=100),
    offset: int = 0,
    search: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Project)

    if search:
        query = query.filter(
            (Project.title.ilike(f"%{search}%")) |
            (Project.description.ilike(f"%{search}%"))
        )

    projects = query.offset(offset).limit(limit).all()
    
    return { "offset": offset, "limit": limit, "projects": projects }

@router.get("/{id}")
def get_project(
    id: int,
    db: Session = Depends(get_db)
):
    query = db.query(Project)

    project = query.get(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project

@router.post("")
def create_project(
    data: dict,
    db: Session = Depends(get_db)
):
    new_project = Project(**data)
    if new_project is None:
        raise HTTPException(status_code=500, detail="JSON in wrong format")

    try:
        db.add(new_project)
        db.commit()

        project_dict = new_project.as_dict()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    return { "status": "created", "project": project_dict }

@router.put("/{id}")
def update_project(
    id: int, data: dict,
    db: Session = Depends(get_db)
):
    try:
        project = db.query(Project).get(id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        for key, value in data.items():
            if hasattr(project, key):
                setattr(project, key, value)

        db.commit()
        updated_project = project.as_dict()

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    return { "status": "updated", "project": updated_project }

@router.delete("/{id}")
def delete_project(
    id: int,
    db: Session = Depends(get_db)
):
    try:
        project = db.query(Project).get(id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        db.delete(project)
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    return { "status": "deleted" }