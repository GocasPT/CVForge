import os

import click
from pathlib import Path
from backend.pipeline import generate_cv
from backend.services.profile_service import ProfileService

PROFILE_PATH = os.environ.get("PROFILE_PATH")

@click.group()
def generate():
    pass


@generate.command("run")
@click.option("--job-file", "-j", type=click.Path(exists=True), help="Ficheiro com a descrição da vaga.")
@click.option("--template", "-t", default="basic", help="Template LaTeX a usar.")
@click.option("--output", "-o", default=None, help="Nome do ficheiro PDF de saída.")
@click.option("--interactive", "-i", is_flag=True, help="Modo interativo (responder a perguntas).")
def run(job_file, template, output, interactive):
    if interactive:
        job_description = click.prompt("📄 Descreve brevemente a vaga (ou cola o texto da descrição):")
    elif job_file:
        job_description = Path(job_file).read_text(encoding="utf-8")
    else:
        click.echo("❌ É necessário usar --job-file ou --interactive.")
        return

    profile_service = ProfileService(Path(PROFILE_PATH))
    if not profile_service.profile_exists():
        click.echo("⚠️  Perfil não encontrado. Usa `cvforge profile set` primeiro.")
        return

    click.echo("🚀 A gerar CV, por favor aguarda...\n")

    pdf_path, selected_projects = generate_cv(
        job_description=job_description,
        template=template
    )

    click.echo("✅ CV gerado com sucesso!\n")
    click.echo("📊 Projetos selecionados:")
    for i, (proj, score) in enumerate(selected_projects, start=1):
        click.echo(f" {i}. {proj['title']} (score: {score:.2f})")

    click.echo(f"\n📁 PDF guardado em: {pdf_path}")
