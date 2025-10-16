from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy.orm import Session
from config import get_db
from models import Experience
from repositories import ExperienceRepo
from schemas import (
    ExperienceCreate,
    ExperienceUpdate,
    ExperienceResponse,
    ExperienceListResponse
)

router = APIRouter()

@router.get("", response_model=ExperienceListResponse, status_code=status.HTTP_200_OK)
def get_projects(
    limit: int = Query(10, ge=1, le=100, description="Number of projects to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    search: str | None = Query(None, description="Search term for position/company/description"),
    db: Session = Depends(get_db)
) -> ExperienceListResponse:
    repo = ExperienceRepo(db)

    with db.begin():
        experiences, total = repo.list(limit=limit, offset=offset, search=search)

    return ExperienceListResponse(
        total=total,
        offset=offset,
        limit=limit,
        experiences=[ExperienceResponse.model_validate(xp) for xp in experiences],
    )


@router.get("/{id}", response_model=ExperienceResponse)
def get_project(
    id: int,
    db: Session = Depends(get_db)
) -> ExperienceResponse:
    repo = ExperienceRepo(db)

    with db.begin():
        experience = repo.get_by_id(id)
    
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience with id {id} not found"
        )
    
    return ExperienceResponse.model_validate(experience)

@router.post("", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ExperienceCreate,
    db: Session = Depends(get_db)
) -> ExperienceResponse:
    repo = ExperienceRepo(db)

    project = Experience(
        position=payload.position,
        company=payload.company,
        location=payload.location,
        start_date=payload.start_date,
        end_date=payload.end_date,
        description=payload.description,
        technologies=payload.technologies,
        achievements=payload.achievements
    )

    with db.begin():
        repo.create(project)

    db.refresh(project)
    return ExperienceResponse.model_validate(project)

@router.put("/{id}", response_model=ExperienceResponse)
def update_project(
    id: int,
    payload: ExperienceUpdate,
    db: Session = Depends(get_db)
) -> ExperienceResponse:
    repo = ExperienceRepo(db)

    project = Experience(
        position=payload.position,
        company=payload.company,
        location=payload.location,
        start_date=payload.start_date,
        end_date=payload.end_date,
        description=payload.description,
        technologies=payload.technologies,
        achievements=payload.achievements
    )

    with db.begin():
        updated_project = repo.update(id, project)
    
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience with id {id} not found"
        )
    
    return ExperienceResponse.model_validate(updated_project)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    id: int,
    db: Session = Depends(get_db)
):
    repo = ExperienceRepo(db)

    with db.begin():
        success = repo.delete(id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience with id {id} not found"
        )
    
    return None