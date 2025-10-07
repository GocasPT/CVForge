import click
from tabulate import tabulate
from datetime import datetime
from backend.config import SessionLocal
from backend.models import Experience


@click.group()
def experience():
    pass


@experience.command()
@click.argument("position")
@click.option("--company", "-c", help="Company name")
@click.option("--location", "-l", help="Location")
@click.option("--start_date", "-s", help="Start date")
@click.option("--end_date", "-e", help="End date")
@click.option("--description", "-d", help="Description")
@click.option("--technologies", "-t", help="Technologies")
@click.option("--achievements", "-a", help="Achievements")
def add(position, company, location, start_date, end_date, description, technologies, achievements):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    except ValueError:
        click.echo("❌ Datas inválidas. Usa o formato YYYY-MM-DD.")
        return

    session = SessionLocal()
    try:
        new_experience = Experience(
            position=position,
            company=company or "",
            location=location,
            start_date=start or datetime.now(),
            end_date=end,
            description=description,
            technologies=technologies or "",
            achievements=achievements or "",
        )
        session.add(new_experience)
        session.commit()
        click.echo(f"✅ Experiência '{position}' adicionada (ID: {new_experience.id})")
    except Exception as e:
        session.rollback()
        click.echo(f"❌ Erro ao adicionar experiência: {e}")
    finally:
        session.close()


@experience.command()
def list():
    session = SessionLocal()
    try:
        experience_list = session.query(Experience).all()
        if not experience_list:
            click.echo("⚠️  Nenhuma experiência encontrada.")
            return

        table = [[e.id, e.position, e.company, e.start_date, e.end_date] for e in experience_list]
        click.echo(tabulate(table, headers=["ID", "Título", "Empresa", "Início", "Fim"], tablefmt="fancy_grid"))
    finally:
        session.close()


@experience.command()
@click.argument("exp_id", type=int)
def remove(exp_id):
    session = SessionLocal()
    try:
        exp = session.query(Experience).filter(Experience.id == exp_id).first()
        if not exp:
            click.echo(f"⚠️  Experiência com ID {exp_id} não encontrada.")
            return
        session.delete(exp)
        session.commit()
        click.echo(f"🗑️  Experiência '{exp.position}' removida com sucesso.")
    except Exception as e:
        session.rollback()
        click.echo(f"❌ Erro ao remover experiência: {e}")
    finally:
        session.close()
