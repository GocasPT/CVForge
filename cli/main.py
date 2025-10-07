import click

from cli.commands import profile, project, experience

@click.group()
def cvforge():
    pass

# Subcomandos
cvforge.add_command(profile)

if __name__ == "__main__":
    cvforge()
