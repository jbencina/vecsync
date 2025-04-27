from openai import AssistantEventHandler, OpenAI
from vecsync.store.openai import OpenAiVectorStore
from vecsync.settings import Settings, SettingExists, SettingMissing
import sys


class OpenAiChat:
    def __init__(self, store_name: str, new_conversation: bool = False):
        self.client = OpenAI()
        self.vector_store = OpenAiVectorStore(store_name)
        self.vector_store.get()

        self.assistant_name = f"vecsync-{self.vector_store.store.name}"
        self.assistant_id = self._get_or_create_assistant()

        self.thread_id = None if new_conversation else self._get_thread_id()

    def _get_thread_id(self) -> str | None:
        settings = Settings()

        match settings["openai_thread_id"]:
            case SettingMissing():
                return None
            case SettingExists() as x:
                print(f"✅ Thread found: {x.value}")
                return x.value

    def _get_or_create_assistant(self):
        settings = Settings()

        match settings["openai_assistant_id"]:
            case SettingExists() as x:
                print(f"✅ Assistant found: {x.value}")
                return x.value
            case _:
                return self._create_assistant()

    def _create_assistant(self) -> str:
        instructions = """You are a helpful research assistant that can search through a large number
        of journals and papers to help answer the user questions. You have been given a file store which contains
        the relevant documents the user is referencing. These documents should be your primary source of information.
        You may only use external knowledge if it is helpful in clarifying questions. It is very important that you
        remain factual and cite information from the sources provided to you in the file store. You are not allowed
        to make up information."""

        assistant = self.client.beta.assistants.create(
            name=self.assistant_name,
            instructions=instructions,
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [self.vector_store.store.id],
                }
            },
            model="gpt-4o-mini",
        )

        settings = Settings()
        del settings["openai_thread_id"]
        del settings["openai_assistant_id"]

        print(f"🖥️ Assistant created: {assistant.name}")
        print(
            f"🔗 Assistant URL: https://platform.openai.com/assistants/{assistant.id}"
        )
        settings["openai_assistant_id"] = assistant.id
        return assistant.id

    def chat(self, prompt: str) -> str:
        settings = Settings()

        if self.thread_id is None:
            thread = self.client.beta.threads.create()
            self.thread_id = thread.id
            print(f"💬 Conversation started: {self.thread_id}")
            settings["openai_thread_id"] = self.thread_id

        _ = self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=prompt,
        )

        with self.client.beta.threads.runs.stream(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            event_handler=PrintHandler(),
        ) as stream:
            stream.until_done()


class PrintHandler(AssistantEventHandler):
    """Helper to print each text delta as it streams."""

    def on_text_delta(self, delta, snapshot):
        # delta.value is the new chunk of text
        sys.stdout.write(delta.value)
        sys.stdout.flush()
