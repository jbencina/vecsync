import click
from termcolor import cprint

from vecsync.store.openai import OpenAiVectorStore


@click.command()
@click.option(
    "--store-name",
    "-s",
    type=str,
    help="Name of the vector store",
    default="default",
)
def list(store_name: str):
    """List files in the remote vector store."""
    store = OpenAiVectorStore(store_name)
    files = store.get_files()

    cprint(f"Files in store {store.name}:", "green")
    for file in files:
        cprint(f" - {file.name}", "yellow")


@click.command()
@click.option(
    "--store-name",
    "-s",
    type=str,
    help="Name of the vector store",
    default="default",
)
def delete(store_name: str):
    """Delete all files in the remote vector store."""
    vstore = OpenAiVectorStore(store_name)
    vstore.delete()


@click.group(name="store")
def group():
    """Commands to manage the vector store."""
    pass


group.add_command(list)
group.add_command(delete)
