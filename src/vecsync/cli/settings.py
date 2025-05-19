import click
from termcolor import colored

from vecsync.settings import Settings


@click.command()
def clear():
    """Clear the settings file."""
    settings = Settings()
    settings.delete()


@click.command()
def show():
    """Get the location and data of the settings file."""
    settings = Settings()
    data = settings.info()
    click.echo(f"Settings file location: {colored(data.location, 'yellow')}")
    click.echo(f"Settings file data:\n{colored(data.data, 'yellow')}")


@click.group(name="settings")
def group():
    """Commands to manage application settings"""
    pass


group.add_command(clear)
group.add_command(show)
