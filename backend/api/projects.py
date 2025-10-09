from fastapi import APIRouter, Query, HTTPException

from backend.config import SessionLocal
from backend.models import Project

router = APIRouter()
session = SessionLocal()

@router.get("/")
def get_projects(
    limit: int = Query(10, ge=1, le=100),
    offset: int = 0,
    search: str | None = None
):
    try:
        query = session.query(Project)

        if search:
            query = query.filter(
                (Project.title.ilike(f"%{search}%")) |
                (Project.description.ilike(f"%{search}%"))
            )

        projects = query.offset(offset).limit(limit).all()
    finally:
        session.close()

    return { "projects": projects, "offset": offset, "limit": limit }

@router.get("/{id}")
def get_project(id: int):
    try:
        query = session.query(Project)

        project = query.get(id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    finally:
        session.close()

    return project

@router.post("/")
def create_project(data: dict):
    new_project = Project(**data)
    if new_project is None:
        raise HTTPException(status_code=500, detail="JSON in wrong format")

    try:
        session.add(new_project)
        session.commit()

        project_dict = new_project.as_dict()
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    finally:
        session.close()

    return { "status": "created", "project": project_dict }

@router.put("/{id}")
def update_project(id: int, data: dict):
    try:
        project = session.query(Project).get(id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        for key, value in data.items():
            if hasattr(project, key):
                setattr(project, key, value)

        session.commit()
        updated_project = project.as_dict()

    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    finally:
        session.close()

    return { "status": "updated", "project": updated_project }

@router.delete("/{id}")
def delete_project(id: int):
    try:
        project = session.query(Project).get(id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        session.delete(project)
        session.commit()

    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    finally:
        session.close()

    return { "status": "deleted" }