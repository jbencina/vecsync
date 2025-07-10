import click

from vecsync.chat.clients.openai import OpenAIClient
from vecsync.chat.interface import ConsoleInterface, GradioInterface
from vecsync.constants import DEFAULT_STORE_NAME


def start_console_chat(store_name: str, prompt_source: str | None = None):
    client = OpenAIClient(store_name=store_name, prompt_source=prompt_source)
    client.connect()

    ui = ConsoleInterface(client)
    print('Type "exit" to quit at any time.')

    while True:
        print()
        prompt = input("> ")
        if prompt.lower() == "exit":
            break
        ui.prompt(prompt)


def start_ui_chat(store_name: str, prompt_source: str | None = None):
    client = OpenAIClient(store_name=store_name, prompt_source=prompt_source)
    client.connect()

    ui = GradioInterface(client)
    ui.chat_interface()


@click.command("chat")
@click.option(
    "--ui",
    "-u",
    is_flag=True,
    help="Spawn an interactive UI instead of a console interface.",
)
@click.option(
    "--prompt",
    "-p",
    type=str,
    help="The path to the prompt source file used when creating a new assistant.",
)
def chat(ui: bool, prompt: str | None):
    """Chat with the assistant."""

    if ui:
        start_ui_chat(DEFAULT_STORE_NAME, prompt)
    else:
        start_console_chat(DEFAULT_STORE_NAME, prompt)
