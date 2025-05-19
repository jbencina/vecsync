import os
from datetime import datetime
from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import BaseModel

import vecsync.chat.clients.openai as client_mod
from vecsync.chat.clients.openai import OpenAIClient, OpenAIHandler
from vecsync.chat.formatter import ConsoleFormatter
from vecsync.store.openai import OpenAiVectorStore


class MockAssistant(BaseModel):
    id: str
    name: str


class MockThread(BaseModel):
    id: str


class MockMessageContentText(BaseModel):
    value: str


class MockMessageContent(BaseModel):
    type: str
    text: MockMessageContentText


class MockMessageData(BaseModel):
    content: list[MockMessageContent]
    created_at: int  # TODO: Check if this is really at both levels
    role: str


class MockMessage(BaseModel):
    data: MockMessageData
    thread_id: str
    created_at: int


class MockThreadMessageResponse(BaseModel):
    thread_id: str
    data: list[MockMessageData]


class MockVectorStore(BaseModel):
    id: str
    name: str


class MockFileUpload(BaseModel):
    id: str
    file: Any


class MockFile(BaseModel):
    id: str
    filename: str


class MockFileDeletedResult(BaseModel):
    deleted: bool


class MockVectorStoreDeletedResult(BaseModel):
    deleted: bool


class MockStreamResponseAnnotation(BaseModel):
    type: str
    text: str


class MockStreamResponseText(BaseModel):
    value: str
    annotations: list[MockStreamResponseAnnotation]


class MockStreamResponseContent(BaseModel):
    type: str
    text: MockStreamResponseText


class MockStreamResponse(BaseModel):
    content: list[MockStreamResponseContent]


def mock_vector_store():
    vector_store = []
    file_store = []
    vector_file_store = []

    def create_vector_store(name):
        store = MockVectorStore(id=f"vector_store_{len(vector_store) + 1}", name=name)
        vector_store.append(store)
        return store

    def delete_vector_store(vector_store_id):
        for store in vector_store:
            if store.id == vector_store_id:
                vector_store.remove(store)
                return MockFileDeletedResult(deleted=True)
        return MockFileDeletedResult(deleted=False)

    def list_vector_stores():
        return vector_store

    def list_files():
        return file_store

    def list_vector_store_files(vector_store_id):
        return vector_file_store

    def delete_vector_store_file(vector_store_id, file_id):
        for vector_file in vector_file_store:
            if vector_file.id == file_id:
                vector_file_store.remove(vector_file)

    def delete_file(file_id):
        for file in file_store:
            if file.id == file_id:
                file_store.remove(file)
                return MockFileDeletedResult(deleted=True)
        return MockFileDeletedResult(deleted=False)

    def create_file(**kwargs):
        base_name = os.path.basename(kwargs["file"].name)
        file = MockFileUpload(id=f"file_{len(file_store) + 1}", file=kwargs["file"])
        file_store.append(MockFile(id=file.id, filename=base_name))
        return file

    def create_and_poll(vector_store_id, file_id):
        for store in vector_store:
            if store.id == vector_store_id:
                vector_file = MockFile(id=file_id, filename=f"file_{file_id}")
                vector_file_store.append(vector_file)
                return vector_file
        return None

    # attach methods
    vs_files_ns = SimpleNamespace()
    vs_files_ns.list = list_vector_store_files
    vs_files_ns.delete = delete_vector_store_file
    vs_files_ns.create_and_poll = create_and_poll

    stores_ns = SimpleNamespace()
    stores_ns.create = create_vector_store
    stores_ns.delete = delete_vector_store
    stores_ns.list = list_vector_stores
    stores_ns.files = vs_files_ns

    files_ns = SimpleNamespace()
    files_ns.list = list_files
    files_ns.delete = delete_file
    files_ns.create = create_file

    # build your “client”
    client = SimpleNamespace()
    client.vector_stores = stores_ns
    client.files = files_ns

    return client


def mock_client_backend():
    # our in‐memory store
    assistant_store = []
    threads_store = []
    message_store = []

    def create_assistant(**kwargs):
        name = kwargs["name"]
        assistant = MockAssistant(id=f"assistant_{name}_{len(assistant_store) + 1}", name=name)
        assistant_store.append(assistant)
        return assistant

    def list_assistants():
        return assistant_store

    def delete_assistant(assistant_id):
        for assistant in assistant_store:
            if assistant.id == assistant_id:
                assistant_store.remove(assistant)

    def create_thread(**kwargs):
        thread = MockThread(id=f"thread_{len(threads_store) + 1}")
        threads_store.append(thread)
        return thread

    def create_message(**kwargs):
        created_at = int(datetime.now().timestamp())

        message = MockMessage(
            created_at=created_at,
            data=MockMessageData(
                created_at=created_at,
                content=[MockMessageContent(type="text", text=MockMessageContentText(value=kwargs["content"]))],
                role=kwargs["role"],
            ),
            thread_id=kwargs["thread_id"],
        )
        message_store.append(message)
        return message

    def list_messages(**kwargs):
        thread_id = kwargs["thread_id"]
        messages = [message.data for message in message_store if message.thread_id == thread_id]
        return MockThreadMessageResponse(thread_id=thread_id, data=messages)

    def stream_response(**kwargs):
        class StreamManager:
            def __init__(self, handler):
                self.handler = handler

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def until_done(self):
                text = """This is a test message from the assistant"""
                for delta in text.split():
                    message = MockStreamResponse(
                        content=[
                            MockStreamResponseContent(
                                type="text", text=MockStreamResponseText(value=delta, annotations=[])
                            )
                        ]
                    )
                    self.handler.on_message_delta(delta=message, snapshot=None)

                self.handler.on_message_done(message=None)

        return StreamManager(handler=kwargs["event_handler"])

    # attach methods
    assistants_ns = SimpleNamespace()
    assistants_ns.create = create_assistant
    assistants_ns.list = list_assistants
    assistants_ns.delete = delete_assistant

    messages_ns = SimpleNamespace()
    messages_ns.create = create_message
    messages_ns.list = list_messages

    runs_ns = SimpleNamespace()
    runs_ns.stream = stream_response

    threads_ns = SimpleNamespace()
    threads_ns.create = create_thread
    threads_ns.messages = messages_ns
    threads_ns.runs = runs_ns

    # build your “client”
    client = SimpleNamespace()
    client.beta = SimpleNamespace()
    client.beta.assistants = assistants_ns
    client.beta.threads = threads_ns

    return client


@pytest.fixture
def mocked_vector_store():
    store = OpenAiVectorStore(name="test_store")
    store.client = mock_vector_store()
    store.create()
    return store


@pytest.fixture
def mocked_client(tmp_path, mocked_vector_store, monkeypatch):
    monkeypatch.setattr(client_mod, "OpenAiVectorStore", lambda store_name: mocked_vector_store)

    settings_path = tmp_path / "settings.json"
    client = OpenAIClient(store_name="test_store", settings_path=settings_path)
    client.client = mock_client_backend()

    return client


@pytest.fixture
def mocked_client_handler():
    return OpenAIHandler(
        files={"file_1", "filename.txt"},
        formatter=ConsoleFormatter(),
    )


@pytest.fixture
def create_test_upload(tmp_path):
    files = set()
    for i in range(3):
        file = tmp_path / f"test_file_{i}.txt"
        files.add(file)
        with open(file, "w") as f:
            f.write(f"This is test file {i}")
    return files
