import click
from commands.profile import profile

@click.group()
def cvforge():
    pass

# Subcomandos
cvforge.add_command(profile)

if __name__ == "__main__":
    cvforge()
