import click
from termcolor import cprint
from vecsync.chat.openai import OpenAiChat
from vecsync.store.openai import OpenAiVectorStore
from vecsync.store.zotero import ZoteroStore
from vecsync.store.file import FileStore
from vecsync.settings import Settings
from dotenv import load_dotenv

# --- Store commands ---

@click.command()
def files():
    store = OpenAiVectorStore("test")
    files = store.get_files()

    cprint(f"Files in store {store.name}:", "green")
    for file in files:
        cprint(f" - {file}", "yellow")

@click.command()
def delete():
    vstore = OpenAiVectorStore("test")
    vstore.delete()

@click.group()
def store():
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
@click.pass_context
def sync(ctx, source: str):
    if source == "file":
        store = FileStore()
    elif source == "zotero":
        store = ZoteroStore.client()
    else:
        raise ValueError("Invalid source. Use 'file' or 'zotero'.")

    vstore = OpenAiVectorStore("test")
    vstore.get_or_create()

    files = store.get_files()

    cprint(f"Syncing {len(files)} files from local to OpenAI", "green")

    result = vstore.sync(files)
    cprint("🏁 Sync results:", "green")
    cprint(f"Saved: {result.files_saved} | Deleted: {result.files_deleted} | Skipped: {result.files_skipped} ", "yellow")
    cprint(f"Remote count: {result.updated_count}", "yellow")
    cprint(f"Duration: {result.duration:.2f} seconds", "yellow")

# --- Assistant commands ---

@click.command("create")
def create_assistant():
    client = OpenAiChat("test")
    name = input("Enter a name for your assistant: ")
    client.create(name)

@click.command("chat")
def chat_assistant():
    client = OpenAiChat("test")

    while True:
        prompt = input("Enter your prompt (or 'exit' to quit): ")
        if prompt.lower() == "exit":
            break
        client.chat(prompt)

@click.group()
def assistant():
    pass

assistant.add_command(create_assistant)
assistant.add_command(chat_assistant)

# --- Settings commands ---

@click.command("delete")
def delete_settings():
    settings = Settings()
    settings.delete()

@click.group()
def settings():
    pass

settings.add_command(delete_settings)

# --- CLI Group (main entry point) ---

@click.group(invoke_without_command=True)
@click.option(
    "--source",
    "-s",
    type=str,
    default="file",
    help="Choose the source (file or zotero).",
)
@click.pass_context
def cli(ctx, source):
    """vecsync CLI tool"""
    load_dotenv(override=True)

    ctx.ensure_object(dict)
    ctx.obj["source"] = source

    if ctx.invoked_subcommand is None:
        # Default to sync if no subcommand
        ctx.invoke(sync, source=source)

cli.add_command(store)
cli.add_command(sync)
cli.add_command(assistant)
cli.add_command(settings)

if __name__ == "__main__":
    cli()
