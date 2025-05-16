import click

from vecsync.cli.assistants import group as assistants_group
from vecsync.cli.chat import chat
from vecsync.cli.settings import group as settings_group
from vecsync.cli.store import group as store_group
from vecsync.cli.sync import sync


@click.group()
def cli():
    """vecsync CLI tool"""
    pass


for group in [assistants_group, store_group, settings_group]:
    cli.add_command(group)

cli.add_command(sync)
cli.add_command(chat)
