import json
from pathlib import Path
from typing import Any
from models import Project
from schemas import ProjectCreate
from config import settings
from services import (
    ProfileService,
    ProjectMatcherService,
    LaTeXService,
    PDFGeneratorService
)

def generate_cv(job_description: str, template: str = "basic") -> tuple[Path, list[tuple[Any, Any]]]:
    print("=========== A iniciar pipeline ===========")

    profile = ProfileService(settings.profile_path).load_profile()
    if not profile:
        pass

    matcher = ProjectMatcherService()
    latex = LaTeXService(settings.templates_dir, settings.generated_dir)
    pdf = PDFGeneratorService(settings.generated_dir)

    print(
        f"Profile: \n\tname: {profile.personal.get('full_name')}\n\temail: {profile.personal.get('email')}\n\t{profile.personal.get('summary')}\n")

    matches = matcher.match_projects(job_description)
    if not matches:
        pass

    print("\nMatching Results:")
    for m in matches:
        print(f"\tRank {m['rank']} | Score {m['score']:.3f} | Projeto: {m['project']['title']}")

    projects = [Project(**p['project']).as_dict() for p in matches]
    
    context = {
        "full_name": profile.personal.get('full_name'),
        "email": profile.personal.get('email'),
        "projects": projects
    }

    print("\nA gerar LaTeX...")
    tex_path = latex.save_rendered(template, context)
    print("✅ LaTeX gerado com sucesso!")

    print("A compilar PDF...")
    pdf_path = pdf.generate(tex_path)
    print("✅ PDF gerado com sucesso!")

    selected_projects = [(m["project"], m["score"]) for m in matches]
    print("=========== A finalizar pipeline ===========")

    return pdf_path, selected_projects
