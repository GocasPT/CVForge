import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator
from pathlib import Path
import datetime
import uuid
from config import settings
from repositories import ProjectRepo
from services import (
    ProfileData,
    ProfileService,
    ProjectMatcherService,
    LaTeXService,
    PDFGeneratorService
)

logger = logging.getLogger(__name__)

router = APIRouter()

class GenerateRequest(BaseModel):
    project_ids: list[int] | None = None
    job_description: str | None = None
    top_n: int = 5
    template: str = "basic"

    @validator('project_ids', 'job_description')
    def check_at_least_one(cls, v, values):
        """Garante que pelo menos um está presente"""
        if not v and not values.get('job_description') and not values.get('project_ids'):
            raise ValueError('Must provide either project_ids or job_description')
        return v


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
        # === ETAPA 1: Obter projetos ===
        if data.project_ids:
            # User selecionou manualmente
            selected_projects = _get_projects_by_ids(data.project_ids)
            scores = [1.0] * len(selected_projects)  # score=1 (manual selection)
        
        elif data.job_description:
            # Auto-matching
            matcher = ProjectMatcherService()
            results = matcher.match_projects(data.job_description, top_n=data.top_n)
            selected_projects = [r["project"] for r in results]
            scores = [r["score"] for r in results]
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide either project_ids or job_description"
            )
        
        if not selected_projects:
            raise HTTPException(
                status_code=400,
                detail="No projects selected or matched"
            )
        
        # === ETAPA 2: Gerar PDF ===
        pdf_path, tex_path = _generate_pdf_from_projects(
            projects=selected_projects,
            template=data.template
        )
        
        # === ETAPA 3: Salvar metadata ===
        cv_id = str(uuid.uuid4())
        meta = {
            "id": cv_id,
            "pdf_path": str(pdf_path),
            "tex_path": str(tex_path),
            "selected_projects": [
                {
                    "id": proj.get("id"),
                    "title": proj.get("title"),
                    "score": float(score)
                }
                for proj, score in zip(selected_projects, scores)
            ],
            "created_at": datetime.datetime.now().isoformat(),
            "success": True,
        }
        
        # Memory management (limita a 50 CVs)
        if len(GENERATED_CVS) >= 50:
            oldest_id = next(iter(GENERATED_CVS))
            GENERATED_CVS.pop(oldest_id)
        
        GENERATED_CVS[cv_id] = meta
        return meta
    
    except Exception as e:
        logger.exception("CV generation failed")
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


# === FUNÇÕES AUXILIARES (adiciona no final) ===

def _get_projects_by_ids(project_ids: list[int]) -> list[dict]:
    """Busca projetos por IDs no DB"""
    repo = ProjectRepo()
    projects = []
    
    for pid in project_ids:
        project = repo.get_by_id(pid)
        if project:
            projects.append({
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "technologies": project.technologies,
                "achievements": project.achievements,
                # ... outros campos
            })
    
    return projects


def _generate_pdf_from_projects(projects: list[dict], template: str) -> tuple[Path, Path]:
    """
    Gera PDF a partir de lista de projetos.
    
    Returns:
        (pdf_path, tex_path)
    """
    # 1. Carrega profile
    profile_service = ProfileService(settings.profile_path)
    profile = profile_service.load_profile()
    if not profile:
        raise ValueError("Profile not found")
    
    # 2. Prepara context para LaTeX
    context = _prepare_latex_context(profile, projects)
    
    # 3. Render template → .tex
    latex_service = LaTeXService(settings.templates_dir, settings.generated_dir)
    tex_path = latex_service.save_rendered(template, context)
    
    # 4. Compila .tex → .pdf
    pdf_service = PDFGeneratorService(settings.generated_dir)
    pdf_path = pdf_service.generate(tex_path)
    
    return pdf_path, tex_path


def _prepare_latex_context(profile: ProfileData, projects: list[dict]) -> dict:
    """
    Converte profile + projects em dict pronto para template LaTeX.
    
    IMPORTANTE: Aqui é onde fixes do LaTeX acontecem.
    """
    from services.latex_service import escape_latex
    
    # Personal info
    personal = profile.personal
    context = {
        "full_name": escape_latex(personal.get("full_name", "")),
        "email": escape_latex(personal.get("email", "")),
        "phone": escape_latex(personal.get("phone", "")),
        "location": escape_latex(personal.get("location", "")),
        "linkedin": escape_latex(personal.get("linkedin", "")),
        "github": escape_latex(personal.get("github", "")),
    }
    
    # Professional summary
    if profile.professional:
        context["summary"] = escape_latex(
            profile.professional.get("summary", "")
        )
    
    # Skills (se existir)
    if profile.skills:
        # Formata skills como string LaTeX
        skills_str = ", ".join([
            escape_latex(skill)
            for category in profile.skills.values()
            for skill in category
        ])
        context["skills"] = skills_str
    
    projects_latex = _format_projects_latex(projects)
    context["projects"] = projects_latex
    
    return context


def _format_projects_latex(projects: list[dict]) -> str:
    """
    Converte lista de projetos em LaTeX string.
    Retorna raw LaTeX (sem escape).
    """
    from services.latex_service import escape_latex
    
    latex_parts = []
    
    for proj in projects:
        title = escape_latex(proj.get("title", "Untitled"))
        desc = escape_latex(proj.get("description", ""))
        techs = escape_latex(", ".join(proj.get("technologies", [])))
        
        # Formata como LaTeX subsection
        latex_parts.append(
            f"\\subsection*{{{title}}}\n"
            f"{desc}\n\n"
            f"\\textit{{Technologies:}} {techs}\n"
        )
    
    return "\n".join(latex_parts)