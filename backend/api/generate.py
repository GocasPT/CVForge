from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import datetime
import uuid
from backend import generate_cv as pipeline

router = APIRouter()

class GenerateRequest(BaseModel):
    job_description: str
    template: str = "basic"


class GenerateResponse(BaseModel):
    id: str
    success: bool
    pdf_path: str
    tex_path: str
    selected_projects: list[dict]
    created_at: str


GENERATED_CVS = {}

@router.post("", response_model=GenerateResponse)
def generate_cv(data: GenerateRequest):
    try:
        pdf_path, selected_projects = pipeline(
            job_description=data.job_description,
            template=data.template
        )

        tex_path = pdf_path.with_suffix('.tex')

        cv_id = str(uuid.uuid4())
        meta = {
            "id": cv_id,
            "pdf_path": str(pdf_path),
            "tex_path": str(tex_path),
            "selected_projects": [
                {
                    "title": proj.get("title"),
                    "description": proj.get("description"),
                    "score": float(score)
                }
                for proj, score in selected_projects
            ],
            "created_at": datetime.datetime.now().isoformat(),
            "success": True,
        }
        GENERATED_CVS[cv_id] = meta

        return meta

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"CV generation failed: {str(e)}"
        )


@router.get("/{id}")
def get_cv_metadata(id: str):
    cv = GENERATED_CVS.get(id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv


@router.get("/file/{id}")
def download_cv_file(id: str):
    cv = GENERATED_CVS.get(id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    pdf_path = Path(cv["pdf_path"])
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"cv_{id}.pdf"
    )