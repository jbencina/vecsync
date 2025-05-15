import click

from vecsync.chat.clients.openai import OpenAIClient
from vecsync.chat.interface import ConsoleInterface, GradioInterface


def start_console_chat(store_name: str, new_conversation: bool):
    client = OpenAIClient(store_name=store_name, new_conversation=new_conversation)
    ui = ConsoleInterface(client)
    print('Type "exit" to quit at any time.')

    while True:
        print()
        prompt = input("> ")
        if prompt.lower() == "exit":
            break
        ui.prompt(prompt)


def start_ui_chat(store_name: str, new_conversation: bool):
    client = OpenAIClient(store_name=store_name, new_conversation=new_conversation)
    ui = GradioInterface(client)
    ui.chat_interface()


@click.command("chat")
@click.option(
    "--new-conversation",
    "-n",
    is_flag=True,
    help="Force the assistant to create a new thread.",
)
@click.option(
    "--use-ui",
    "-u",
    is_flag=True,
    help="Spawn an interactive UI instead of a console interface.",
)
@click.option(
    "--store-name",
    "-s",
    type=str,
    help="Name of the vector store",
    default="default",
)
def chat(new_conversation: bool, use_ui: bool, store_name: str):
    """Chat with the assistant."""

    if use_ui:
        start_ui_chat(store_name, new_conversation)
    else:
        start_console_chat(store_name, new_conversation)
