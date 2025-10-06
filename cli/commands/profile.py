import os

import click
from pathlib import Path
from backend.services.profile_service import ProfileService

service = ProfileService(Path(os.environ.get("PROFILE_PATH")))

@click.group()
def profile():
    pass

@profile.command()
def show():
    summary = service.get_profile_summary()
    if summary.get("error"):
        click.echo(f"⚠️  {summary['error']}")
    else:
        click.echo(f"👤 {summary['full_name']}")
        click.echo(f"📧 {summary['email']}")
        click.echo(f"🧠 Skills categories: {summary['skills_categories']}")


@profile.command()
@click.option("--name", help="Nome completo do utilizador.")
@click.option("--email", help="Email profissional.")
def set(name, email):
    profile_data = service.load_profile()

    if name:
        profile_data.personal["full_name"] = name
    if email:
        profile_data.personal["email"] = email

    if service.save_profile(profile_data):
        click.echo("✅ Perfil atualizado com sucesso.")
    else:
        click.echo("❌ Erro ao guardar o perfil.")
