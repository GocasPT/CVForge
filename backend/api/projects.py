from fastapi import APIRouter, Query, HTTPException, status
from services import ProjectMatcherService
from models import Project
from repositories import ProjectRepo
from schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectMatchs
)

router = APIRouter()

@router.get("", response_model=ProjectListResponse, status_code=status.HTTP_200_OK)
def get_projects(
    limit: int = Query(10, ge=1, le=100, description="Number of projects to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    search: str | None = Query(None, description="Search term for title/description"),
) -> ProjectListResponse:
    repo = ProjectRepo()

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
) -> ProjectResponse:
    repo = ProjectRepo()

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
) -> ProjectResponse:
    repo = ProjectRepo()

    project = Project(
        title=payload.title,
        description=payload.description,
        technologies=payload.technologies,
        achievements=payload.achievements,
        duration=payload.duration,
        role=payload.role
    )

    repo.create(project)

    return ProjectResponse.model_validate(project)

@router.put("/{id}", response_model=ProjectResponse)
def update_project(
    id: int,
    payload: ProjectUpdate,
) -> ProjectResponse:
    repo = ProjectRepo()

    project = Project(
        title=payload.title,
        description=payload.description,
        technologies=payload.technologies,
        achievements=payload.achievements,
        duration=payload.duration,
        role=payload.role
    )

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
):
    repo = ProjectRepo()

    success = repo.delete(id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {id} not found"
        )
    
    return None


@router.post("/match", status_code=status.HTTP_200_OK)
def match_projects_for_job(
    payload: ProjectMatchs
):
    """
    Match projects to job description using semantic similarity.
    Returns ranked list of projects with scores.
    """

    # job_description: str,
    # top_n: int = Query(5, ge=1, le=20, description="Number of projects to return")

    matcher = ProjectMatcherService()
    results = matcher.match_projects(payload.job_description, top_n=payload.top_n)
    
    # Transform results para formato API-friendly
    matches = []
    for r in results:
        project = r["project"]
        matches.append({
            "id": project.get("id"),
            "title": project.get("title"),
            "description": project.get("description"),
            "technologies": project.get("technologies", []),
            "score": r["score"],
            "rank": r["rank"]
        })
    
    return {
        "job_description": payload.job_description[:100] + "...",
        "matches": matches,
        "total_matches": len(matches)
    }