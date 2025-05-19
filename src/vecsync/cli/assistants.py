import click
from termcolor import cprint

from vecsync.chat.clients.openai import OpenAIClient
from vecsync.constants import DEFAULT_STORE_NAME


@click.command(name="list")
def list_assistants():
    """List all vecync assistants in the OpenAI account."""
    client = OpenAIClient(store_name=DEFAULT_STORE_NAME)
    assistants = client.list_assistants()

    if len(assistants) == 0:
        cprint("No assistants found.", "green", attrs=["bold"])
    else:
        cprint("Assistants in your OpenAI account:", "green", attrs=["bold"])
        for i, assistant in enumerate(assistants):
            cprint(f"  {i + 1}. Name: {assistant.name} ({assistant.id})", "yellow")


@click.command()
def clean():
    """Clean up vecsync assistants in the OpenAI account."""
    client = OpenAIClient(store_name=DEFAULT_STORE_NAME)
    assistants = client.list_assistants()

    if len(assistants) == 0:
        cprint("No deletable assistants found.", "green", attrs=["bold"])
        return

    cprint("Assistants in your OpenAI account:", "green", attrs=["bold"])
    for i, assistant in enumerate(assistants):
        cprint(f"  {i + 1}. Name: {assistant.name} ({assistant.id})", "yellow")
    cprint("Would you like to delete the following assistants? [y/N] ", "red", end="")

    confirm = input().strip().lower()

    while confirm not in ["y", "n", ""]:
        cprint("Please enter 'y' or 'n': ", "red", end="")
        confirm = input().strip().lower()

    if confirm in ["", "n"]:
        cprint("Aborting...", "green", attrs=["bold"])
        return

    for assistant in assistants:
        cprint(f"Deleting assistant {assistant.name} ({assistant.id})...", "red", attrs=["bold"])
        client.delete_assistant(assistant.id)


@click.group(name="assistants")
def group():
    """Commands to manage assistants"""
    pass


group.add_command(list_assistants)
group.add_command(clean)
