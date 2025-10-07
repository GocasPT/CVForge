import click

from cli.commands import profile, project, experience, template, generate

@click.group()
def cvforge():
    pass

# Subcomandos
cvforge.add_command(profile)
cvforge.add_command(project)
cvforge.add_command(experience)
cvforge.add_command(template)
cvforge.add_command(generate)

if __name__ == "__main__":
    cvforge()
