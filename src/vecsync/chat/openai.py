from openai import AssistantEventHandler, OpenAI
from vecsync.store.openai import OpenAiVectorStore
import sys


class OpenAiChat:
    def __init__(self, store_name: str):
        self.client = OpenAI()
        self.vector_store = OpenAiVectorStore(store_name)
        self.vector_store.get()

        self.assistant_name = f"vecsync-{self.vector_store.store.name}"
        self.assistant_id = self._get_or_create_assistant()

        self.thread = None

    def _get_or_create_assistant(self):
        existing_assistants = self.client.beta.assistants.list()

        for assistant in existing_assistants:
            if assistant.name == self.assistant_name:
                print(f"✅ Assistant found: {assistant.id}")
                return assistant.id

        return self._create_assistant()

    def _create_assistant(self) -> str:
        instructions = """You are a helpful research assistant that can search through a large number
        of journals and papers to find revelant information. It is very important that you
        remain factual and cite information from the sources provided to you in the 
        vector store. You are not allowed to make up information"""

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

        print(f"✅ Assistant created: {assistant.name}")
        print(
            f"🔗 Assistant URL: https://platform.openai.com/assistants/{assistant.id}"
        )
        return assistant.id

    def chat(self, prompt: str) -> str:
        if self.thread is None:
            self.thread = self.client.beta.threads.create()

        _ = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=prompt,
        )

        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
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
