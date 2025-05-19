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
    """Handler for OpenAI API events.

    This class is used to handle streaming events from the OpenAI API. Internally, it puts all streaming
    chunks into a Queue which allows for the streaming to be consumed in real time by other functions.

    Parameters
    ----------
    files : dict[str, str]
        A dictionary of file IDs and their corresponding names. This is used to format the citations
        in the response.
    formatter : ConsoleFormatter | GradioFormatter
        The formatter to use for formatting the output of the response. This can be either a
        ConsoleFormatter or GradioFormatter.
    """

    def __init__(self, files: dict[str, str], formatter: ConsoleFormatter | GradioFormatter):
        super().__init__()
        self.files = files
        self.queue = Queue()
        self.annotations = {}
        self.active = True
        self.formatter = formatter

    def on_message_delta(self, delta, snapshot):
        # Handle the response chunk
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
        # Append citations at the end of the response
        text = self.formatter.get_references(self.annotations, self.files)
        if len(text) > 0:
            self.queue.put(text)
        self.active = False

    def consume_queue(self, timeout: float = 1.0):
        """Consume chunks from the queue.

        Parameters
        ----------
        timeout : float
            The timeout seconds for the queue. This is used to prevent blocking if there are no chunks
            available in the queue.

        Yields
        ------
        str
            The chunks of text from the queue. This will yield until the queue is empty or the
            active flag is set to False.
        """

        while self.active or not self.queue.empty():
            try:
                chunk = self.queue.get(timeout=timeout)
            except Empty:
                continue
            if chunk is None:
                break
            yield chunk


class OpenAIClient:
    """OpenAI client for interacting with the OpenAI API.

    This client is used to send messages to the OpenAI API and receive responses.

    Parameters
    ----------
    store_name : str
        The name of the vector store to use for this client. The named assistant will
        be created in the form of "vecsync-{store_name}".
    settings_path : str | None
        The path to the settings file. If None, the default settings file will be used.
        This is used to store the thread ID for the current conversation.
    """

    def __init__(self, store_name: str, settings_path: str | None = None):
        self.client = OpenAI()
        self.store_name = store_name
        self.assistant_name = f"vecsync-{store_name}"
        self.connected = False
        self.settings_path = settings_path

    def connect(self):
        """Connect to the OpenAI API and load the assistant and thread.

        There are four independent entitites in the OpenAI API:
        1. Files: User files are uploaded to OpenAI and exist as an artifact which can be used in
           several places. The file references are loaded here for translating ciation references.
        2. Vector Store: The vector store is a collection of files which are used for RAG search
           by the assistant. A vector store can be assigned to multiple assistants.
        3. Assistant: The assistant is the entity which is used to interact with the OpenAI API.
           We currently only support one assistant per OpenAI account.
        4. Thread: The thread is the conversation history which is used to store messages between the
           user and assistant. Threads are created whenever a new assistant is created, the user
           deletes their settings file, or the user runs the application on a different machine.
        """
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
        """Clear all OpenAI client state."""
        self.assistant_id = None
        self.thread_id = None
        self.files = None
        self.vector_store = None
        self.connected = False

    def _get_thread_id(self) -> str:
        """Locates or creates the thread ID

        Thread IDs are stored locally in the user settings file. The ID is loaded from settings and
        is created if it doesn't exist.

        Returns
        -------
        str
            The thread ID for the current conversation.
        """
        settings = Settings(path=self.settings_path)

        # TODO: Ideally we would grab the thread ID from OpenAI but there doesn't seem to be
        # a way to do that. So we are storing it in the settings file for now.
        match settings["openai_thread_id"]:
            case SettingMissing():
                return self._create_thread()
            case SettingExists() as x:
                print(f"✅ Thread found: {x.value}")
                return x.value

    def _get_assistant_id(self) -> str:
        """Locates or creates the assistant ID

        Assistant IDs are stored in the OpenAI account. The ID is loaded from the account and is created
        if it doesn't exist. There should only be one assistant per account at any point in time. This step
        performs a cleanup check if multiple assistants are found.

        Returns
        -------
        str
            The assistant ID for the current conversation.
        """
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
        """Creates a new assistant in the OpenAI account.

        The assistant is created with the name "vecsync-{store_name}" and is attached to the
        user's vector store.

        Returns
        -------
        str
            The assistant ID for the current conversation.
        """

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

        settings = Settings(path=self.settings_path)
        del settings["openai_thread_id"]

        print(f"🖥️ Assistant created: {assistant.name}")
        print(f"🔗 Assistant URL: https://platform.openai.com/assistants/{assistant.id}")
        return assistant.id

    def _create_thread(self) -> str:
        """Creates a new thread in the OpenAI account.

        The new thread ID is stored in the local settings file since OpenAI doesn't provide a way to
        remotely access the thread ID.

        Returns
        -------
        str
            The thread ID for the current conversation.
        """

        thread = self.client.beta.threads.create()
        print(f"💬 Conversation started: {thread.id}")
        settings = Settings(path=self.settings_path)
        settings["openai_thread_id"] = thread.id
        return thread.id

    def load_history(self) -> list[dict[str, str]]:
        """Fetch all prior messages in this thread

        This method loads the conversation history from the OpenAI API. The messages are sorted
        by their creation time.

        Returns
        -------
        list[dict[str, str]]
            A list of dictionaries containing the role and content of each message.
            The role is either "user" or "assistant".
        """

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

    def send_message(self, prompt: str):
        """Send a message to the OpenAI thread.

        Parameters
        ----------
        prompt : str
            The message to send to the OpenAI thread.
        """

        if not self.connected:
            self.connect()

        return self.client.beta.threads.messages.create(thread_id=self.thread_id, role="user", content=prompt)

    def stream_response(self, thread_id: str, assistant_id: str, handler):
        """Generate a thread run and stream the response.

        Parameters
        ----------
        thread_id : str
            The ID of the thread to stream the response from.
        assistant_id : str
            The ID of the assistant to stream the response from.
        handler : AssistantEventHandler
            The event handler to use for processing the response.
        """

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
        self.disconnect()
