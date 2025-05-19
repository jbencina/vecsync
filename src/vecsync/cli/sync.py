import click
from termcolor import cprint

from vecsync.constants import DEFAULT_STORE_NAME
from vecsync.store.file import FileStore
from vecsync.store.openai import OpenAiVectorStore
from vecsync.store.zotero import ZoteroStore


@click.command()
@click.option(
    "--source",
    type=str,
    default="file",
    help="Choose the source (file or zotero).",
)
def sync(source: str):
    """Sync files from local to remote vector store."""
    if source == "file":
        store = FileStore()
    elif source == "zotero":
        try:
            store = ZoteroStore.client()
        except FileNotFoundError as e:
            cprint(f'Zotero not found at "{str(e)}". Aborting.', "red")
            return
    else:
        raise ValueError("Invalid source. Use 'file' or 'zotero'.")

    vstore = OpenAiVectorStore(DEFAULT_STORE_NAME)
    vstore.get_or_create()

    files = store.get_files()

    cprint(f"Syncing {len(files)} files from local to OpenAI", "green")

    result = vstore.sync(files)
    cprint("🏁 Sync results:", "green")
    cprint(
        f"Saved: {result.files_saved} | Deleted: {result.files_deleted} | Skipped: {result.files_skipped} ",
        "yellow",
    )
    cprint(f"Remote count: {result.remote_count}", "yellow")
    cprint(f"Duration: {result.duration:.2f} seconds", "yellow")
