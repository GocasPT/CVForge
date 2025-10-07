import click

from cli.commands import profile, project, experience

@click.group()
def cvforge():
    pass

# Subcomandos
cvforge.add_command(profile)
cvforge.add_command(project)
cvforge.add_command(experience)

if __name__ == "__main__":
    cvforge()
