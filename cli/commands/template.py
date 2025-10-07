import os

import click
from pathlib import Path

from services import LaTeXService

latex = LaTeXService(Path("backend/templates"), Path(os.environ.get("GENERATED_DIR")))

@click.group()
def template():
    pass


@template.command("list")
def list_templates():
    templates = latex.get_available_templates()
    if not templates:
        click.echo("⚠️  Nenhum template encontrado.")
        return

    click.echo("📄 Templates disponíveis:")
    for t in templates:
        click.echo(f" - {t}")
