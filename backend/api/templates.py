import os
from fastapi import APIRouter
from backend.config import settings
from backend.services import LaTeXService

router = APIRouter()
TEMPLATES_PATH = settings.templates_dir
latex_service = LaTeXService(TEMPLATES_PATH, settings.generated_dir)

@router.get("")
def get_templates():
    templates = [f for f in os.listdir(TEMPLATES_PATH) if f.endswith(".tex")]
    return {"templates": templates}

@router.get("/{name}")
def get_template(name: str):
    template = TEMPLATES_PATH / f"{name}.tex"
    return template.read_text()

@router.post("")
def preview(data: dict):
    template_name = data.get("template", "basic")
    rendered = latex_service.render(template_name, data)
    return {"success": True, "rendered_tex": rendered}
