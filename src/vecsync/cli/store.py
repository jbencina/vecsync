import click
from termcolor import cprint

from vecsync.constants import DEFAULT_STORE_NAME
from vecsync.store.openai import OpenAiVectorStore


@click.command(name="list")
def list_stores():
    """List files in the remote vector store."""
    store = OpenAiVectorStore(DEFAULT_STORE_NAME)
    files = store.get_files()

    num_total = len(files)

    cprint(f"{num_total} Files in store '{store.name}':", "green")
    for file in files:
        cprint(f"\t✅{file.name}", "yellow")


@click.command()
def delete():
    """Delete all files in the remote vector store."""
    vstore = OpenAiVectorStore(DEFAULT_STORE_NAME)
    vstore.delete()


@click.group(name="store")
def group():
    """Commands to manage the vector store."""
    pass


group.add_command(list_stores)
group.add_command(delete)
