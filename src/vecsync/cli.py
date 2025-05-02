import click
from dotenv import load_dotenv
from termcolor import cprint

from vecsync.chat.clients.openai import OpenAIClient
from vecsync.chat.interface import ConsoleInterface, GradioInterface
from vecsync.settings import Settings
from vecsync.store.file import FileStore
from vecsync.store.openai import OpenAiVectorStore
from vecsync.store.zotero import ZoteroStore

# --- Store commands ---
load_dotenv(override=True)


@click.command()
def files():
    """List files in the remote vector store."""
    store = OpenAiVectorStore("test")
    files = store.get_files()

    cprint(f"Files in store {store.name}:", "green")
    for file in files:
        cprint(f" - {file.name}", "yellow")


@click.command()
def delete():
    """Delete all files in the remote vector store."""
    vstore = OpenAiVectorStore("test")
    vstore.delete()


@click.group()
def store():
    """Manage the vector store."""
    pass


store.add_command(files)
store.add_command(delete)

# --- Sync command (default behavior) ---


@click.command()
@click.option(
    "--source",
    "-s",
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

    vstore = OpenAiVectorStore("test")
    vstore.get_or_create()

    files = store.get_files()

    cprint(f"Synching {len(files)} files from local to OpenAI", "green")

    result = vstore.sync(files)
    cprint("🏁 Sync results:", "green")
    cprint(
        f"Saved: {result.files_saved} | Deleted: {result.files_deleted} | Skipped: {result.files_skipped} ",
        "yellow",
    )
    cprint(f"Remote count: {result.updated_count}", "yellow")
    cprint(f"Duration: {result.duration:.2f} seconds", "yellow")


# --- Assistant commands ---


@click.command("chat")
@click.option(
    "--new-conversation",
    "-n",
    is_flag=True,
    help="Force the assistant to create a new thread.",
)
def chat_assistant(new_conversation: bool):
    """Chat with the assistant."""
    client = OpenAIClient("test", new_conversation=new_conversation)
    ui = ConsoleInterface(client)
    print('Type "exit" to quit at any time.')

    while True:
        print()
        prompt = input("> ")
        if prompt.lower() == "exit":
            break
        ui.prompt(prompt)


@click.command("ui")
def chat_ui():
    client = OpenAIClient("test")
    ui = GradioInterface(client)
    ui.chat_interface()


@click.group()
def assistant():
    """Assistant commands."""
    pass


assistant.add_command(chat_assistant)
assistant.add_command(chat_ui)

# --- Settings commands ---


@click.command("clear")
def clear_settings():
    """Clear the settings file."""
    settings = Settings()
    settings.delete()


@click.group()
def settings():
    pass


settings.add_command(clear_settings)

# --- CLI Group (main entry point) ---


@click.group()
def cli():
    """vecsync CLI tool"""
    pass


cli.add_command(store)
cli.add_command(sync)
cli.add_command(assistant)
cli.add_command(settings)

if __name__ == "__main__":
    cli()
