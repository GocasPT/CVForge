from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy.orm import Session
from config import get_db
from models import Project
from repositories import ProjectRepo
from schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse
)

router = APIRouter()

@router.get("", response_model=ProjectListResponse, status_code=status.HTTP_200_OK)
def get_projects(
    limit: int = Query(10, ge=1, le=100, description="Number of projects to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    search: str | None = Query(None, description="Search term for title/description"),
    db: Session = Depends(get_db)
) -> ProjectListResponse:
    repo = ProjectRepo(db)

    with db.begin():
        projects, total = repo.list(limit=limit, offset=offset, search=search)

    return ProjectListResponse(
        total=total,
        offset=offset,
        limit=limit,
        projects=[ProjectResponse.model_validate(p) for p in projects],
    )


@router.get("/{id}", response_model=ProjectResponse)
def get_project(
    id: int,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    repo = ProjectRepo(db)

    with db.begin():
        project = repo.get_by_id(id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {id} not found"
        )
    
    return ProjectResponse.model_validate(project)

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    repo = ProjectRepo(db)

    project = Project(
        title=payload.title,
        description=payload.description,
        technologies=payload.technologies,
        achievements=payload.achievements,
        duration=payload.duration,
        role=payload.role
    )

    with db.begin():
        repo.create(project)

    db.refresh(project)
    return ProjectResponse.model_validate(project)

@router.put("/{id}", response_model=ProjectResponse)
def update_project(
    id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    repo = ProjectRepo(db)

    project = Project(
        title=payload.title,
        description=payload.description,
        technologies=payload.technologies,
        achievements=payload.achievements,
        duration=payload.duration,
        role=payload.role
    )

    with db.begin():
        updated_project = repo.update(id, project)
    
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {id} not found"
        )
    
    return ProjectResponse.model_validate(updated_project)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    id: int,
    db: Session = Depends(get_db)
):
    repo = ProjectRepo(db)

    with db.begin():
        success = repo.delete(id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {id} not found"
        )
    
    return None