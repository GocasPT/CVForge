from typing import List
from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy.orm import Session
from backend.config import get_db
from backend.repositories import ProjectRepository
from backend.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse
)

router = APIRouter()

def get_project_repository(db: Session = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)

@router.get("", response_model=ProjectListResponse)
def get_projects(
    limit: int = Query(10, ge=1, le=100, description="Number of projects to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    search: str | None = Query(None, description="Search term for title/description"),
    repo: ProjectRepository = Depends(get_project_repository)
) -> ProjectListResponse:
    projects, total = repo.get_all(limit=limit, offset=offset, search=search)
    
    return ProjectListResponse(
        total=total,
        offset=offset,
        limit=limit,
        projects=[ProjectResponse.model_validate(p) for p in projects],
    )

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    repo: ProjectRepository = Depends(get_project_repository)
) -> ProjectResponse:
    project = repo.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    return project

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    repo: ProjectRepository = Depends(get_project_repository)
) -> ProjectResponse:
    try:
        new_project = repo.create(project_data)
        return new_project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    repo: ProjectRepository = Depends(get_project_repository)
) -> ProjectResponse:
    updated_project = repo.update(project_id, project_data)
    
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    return updated_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    repo: ProjectRepository = Depends(get_project_repository)
):
    success = repo.delete(project_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    return None