import click

from vecsync.settings import Settings


@click.command("clear")
def clear_settings():
    """Clear the settings file."""
    settings = Settings()
    settings.delete()


@click.group(name="settings")
def group():
    """Commands to manage application settings"""
    pass


group.add_command(clear_settings)
