import click
from tabulate import tabulate
from backend.config import SessionLocal
from backend.models import Project


@click.group()
def project():
    pass


@project.command()
@click.argument("title")
@click.option("--description", "-d", help="Descrição do projeto.")
@click.option("--tech", "-t", help="Tecnologias usadas.")
@click.option("--achievements", "-a", help="Achievements usadas.")
@click.option("--duration", "-D", help="Duração")
@click.option("--role", "-r", help="Role.")
def add(title, description, tech, achievements, duration, role):
    session = SessionLocal()
    try:
        new_project = Project(
            title=title,
            description=description or "",
            technologies=tech or "",
            achievements=achievements or "",
            duration=duration or "",
            role=role,
        )
        session.add(new_project)
        session.commit()
        click.echo(f"✅ Projeto '{title}' adicionado com sucesso (ID: {new_project.id})")
    except Exception as e:
        session.rollback()
        click.echo(f"❌ Erro ao adicionar projeto: {e}")
    finally:
        session.close()


@project.command()
def list():
    session = SessionLocal()
    try:
        projects = session.query(Project).all()
        if not projects:
            click.echo("⚠️  Nenhum projeto encontrado.")
            return

        table = [[p.id, p.title, p.description[:50], getattr(p, "technologies", "-")] for p in projects]
        click.echo(tabulate(table, headers=["ID", "Título", "Descrição", "Tech"], tablefmt="fancy_grid"))
    finally:
        session.close()


@project.command()
@click.argument("project_id", type=int)
def remove(project_id):
    session = SessionLocal()
    try:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            click.echo(f"⚠️  Projeto com ID {project_id} não encontrado.")
            return
        session.delete(project)
        session.commit()
        click.echo(f"🗑️  Projeto '{project.title}' removido com sucesso.")
    except Exception as e:
        session.rollback()
        click.echo(f"❌ Erro ao remover projeto: {e}")
    finally:
        session.close()
