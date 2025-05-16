from queue import Empty, Queue

from openai import AssistantEventHandler, OpenAI
from termcolor import cprint

from vecsync.chat.clients.base import Assistant
from vecsync.chat.formatter import ConsoleFormatter, GradioFormatter
from vecsync.settings import SettingExists, SettingMissing, Settings
from vecsync.store.openai import OpenAiVectorStore


# TODO: This class will likely be refactored into common class across other client types. However
# since we only have OpenAI at the moment, we'll keep it here for now.
class OpenAIHandler(AssistantEventHandler):
    def __init__(self, files: dict[str, str], formatter: ConsoleFormatter | GradioFormatter):
        super().__init__()
        self.files = files
        self.queue = Queue()
        self.annotations = {}
        self.active = True
        self.formatter = formatter

    def on_message_delta(self, delta, snapshot):
        delta_annotations = {}
        text_chunks = []

        for content in delta.content:
            if content.type == "text":
                if content.text.annotations:
                    for annotation in content.text.annotations:
                        if annotation.type == "file_citation":
                            delta_annotations[annotation.text] = annotation.file_citation.file_id

                text = content.text.value

                if len(delta_annotations) > 0:
                    for ref_id, file_id in delta_annotations.items():
                        # TODO: If there are multiple references to the same file then it prints the id several
                        # times such as "[1] [1] [1]". This should be fixed.
                        self.annotations.setdefault(file_id, len(self.annotations) + 1)
                        citation = self.formatter.format_citation(self.annotations[file_id])
                        text = text.replace(ref_id, citation)

                text_chunks.append(text)
        self.queue.put("".join(text_chunks))

    def on_message_done(self, message):
        text = self.formatter.get_references(self.annotations, self.files)
        self.queue.put(text)
        self.active = False

    def consume_queue(self, timeout: float = 1.0):
        """Pulls from handler.queue in real time, calls write_fn(text)."""
        while self.active or not self.queue.empty():
            try:
                chunk = self.queue.get(timeout=timeout)
            except Empty:
                continue
            if chunk is None:
                break
            yield chunk


class OpenAIClient:
    def __init__(self, store_name: str):
        self.client = OpenAI()
        self.store_name = store_name
        self.assistant_name = f"vecsync-{store_name}"
        self.connected = False

    def connect(self):
        # Connect to the OpenAI vector store
        self.vector_store = OpenAiVectorStore(self.store_name)
        self.vector_store.get()

        # Load the assistant and thread
        self.assistant_id = self._get_assistant_id()
        self.thread_id = self._get_thread_id()

        # Load the files in the vector store
        self.files = {f.id: f.name for f in self.vector_store.get_files()}
        self.connected = True

    def disconnect(self):
        self.assistant_id = None
        self.thread_id = None
        self.files = None
        self.vector_store = None
        self.connected = False

    def _get_thread_id(self) -> str | None:
        settings = Settings()

        # TODO: Ideally we would grab the thread ID from OpenAI but there doesn't seem to be
        # a way to do that. So we are storing it in the settings file for now.
        match settings["openai_thread_id"]:
            case SettingMissing():
                return self._create_thread()
            case SettingExists() as x:
                print(f"✅ Thread found: {x.value}")
                return x.value

    def _get_assistant_id(self):
        # Check if the assistant already exists
        existing_assistants = self.list_assistants()
        count_assistants = len(existing_assistants)

        if count_assistants > 1:
            # We only allow for one assistant per account at this time
            # This state shouldn't happen, but if it does, we need to remove the extras
            # to keep things clean

            count_extra = count_assistants - 1
            cprint(f"⚠️ Multiple vecsync assistants found in account. Cleaning up {count_extra} extras.", "yellow")

            for assistant in existing_assistants[1:]:
                self.delete_assistant(assistant.id)

        if count_assistants > 0:
            id = existing_assistants[0].id
            print(f"✅ Assistant found remotely: {id}")
            return id
        else:
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

        print(f"🖥️ Assistant created: {assistant.name}")
        print(f"🔗 Assistant URL: https://platform.openai.com/assistants/{assistant.id}")
        return assistant.id

    def _create_thread(self) -> str:
        thread = self.client.beta.threads.create()
        print(f"💬 Conversation started: {thread.id}")
        settings = Settings()
        settings["openai_thread_id"] = thread.id
        return thread.id

    def load_history(self) -> list[dict[str, str]]:
        """Fetch all prior messages in this thread"""
        if not self.connected:
            self.connect()

        history = []
        if self.thread_id is not None:
            resp = self.client.beta.threads.messages.list(thread_id=self.thread_id)
            resp_data = sorted(resp.data, key=lambda x: x.created_at)

            for msg in resp_data:
                content = ""
                for c in msg.content:
                    if c.type == "text":
                        content += c.text.value

                history.append(dict(role=msg.role, content=content))

        return history

    def _run_stream(self, handler: OpenAIHandler):
        with self.client.beta.threads.runs.stream(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            event_handler=handler,
        ) as stream:
            stream.until_done()

    def send_message(self, prompt: str):
        if not self.connected:
            self.connect()

        return self.client.beta.threads.messages.create(thread_id=self.thread_id, role="user", content=prompt)

    def stream_response(self, thread_id: str, assistant_id: str, handler):
        with self.client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,
            event_handler=handler,
        ) as stream:
            stream.until_done()

    def list_assistants(self) -> list[Assistant]:
        """List all vecsync assistants in the OpenAI account.

        This only returns vecsync assistants which are prefixed with "vecsync-". There should
        only be one assistant per account, but this method is here to help with cleanup if
        multiple assistants are created.

        Returns:
            list[Assistant]: A list of Assistant objects.
        """
        results = []

        for assistant in self.client.beta.assistants.list():
            if assistant.name.startswith("vecsync-"):
                results.append(Assistant(id=assistant.id, name=assistant.name))

        return results

    def delete_assistant(self, assistant_id: str):
        """Delete an assistant from the OpenAI account.

        Args:
            assistant_id (str): The ID of the assistant to delete.
        """
        self.client.beta.assistants.delete(assistant_id)

        if self.assistant_id == assistant_id:
            # If the assistant we just deleted is the one we are using, then we need to clear the settings
            settings = Settings()
            del settings["openai_thread_id"]
            self.disconnect()
