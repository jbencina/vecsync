from datetime import datetime
from types import SimpleNamespace

import pytest
from pydantic import BaseModel

import vecsync.chat.clients.openai as client_mod
from vecsync.chat.clients.openai import OpenAIClient
from vecsync.settings import Settings
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
    content: MockMessageContent


class MockMessage(BaseModel):
    created_at: int
    data: MockMessageData
    thread_id: str


class MockVectorStore(BaseModel):
    id: str
    name: str


def mock_vector_store():
    vector_store = []
    file_store = []
    vector_file_store = []

    def create_vector_store(name):
        store = MockVectorStore(id=f"vector_store_{len(vector_store) + 1}", name=name)
        vector_store.append(store)
        return store

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

    # attach methods
    vs_files_ns = SimpleNamespace()
    vs_files_ns.list = list_vector_store_files
    vs_files_ns.delete = delete_vector_store_file

    stores_ns = SimpleNamespace()
    stores_ns.create = create_vector_store
    stores_ns.list = list_vector_stores
    stores_ns.files = vs_files_ns

    files_ns = SimpleNamespace()
    files_ns.list = list_files
    files_ns.delete = delete_file

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
                content=MockMessageContent(type="text", text=MockMessageContentText(value=kwargs["content"]))
            ),
            thread_id=kwargs["thread_id"],
        )
        message_store.append(message)
        return message

    # attach methods
    assistants_ns = SimpleNamespace()
    assistants_ns.create = create_assistant
    assistants_ns.list = list_assistants
    assistants_ns.delete = delete_assistant

    threads_ns = SimpleNamespace()
    threads_ns.create = create_thread

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


def test_list_assistants(mocked_client):
    mocked_client.client.beta.assistants.create(name="vecsync-1")
    mocked_client.client.beta.assistants.create(name="vecsync-2")
    mocked_client.client.beta.assistants.create(name="other-3")

    assistants = mocked_client.list_assistants()

    assert len(assistants) == 2


def test_delete_assistant(mocked_client):
    assistant = mocked_client.client.beta.assistants.create(name="vecsync-1")
    mocked_client.client.beta.assistants.create(name="vecsync-2")

    mocked_client.delete_assistant(assistant.id)

    assert len(mocked_client.list_assistants()) == 1


def test_create_thread(mocked_client):
    thread_id = mocked_client._create_thread()
    assert thread_id == "thread_1"


def test_get_thread_id_new(mocked_client):
    thread_id = mocked_client._get_thread_id()
    assert thread_id == "thread_1"


def test_get_thread_id_existing(mocked_client):
    settings = Settings(path=mocked_client.settings_path)
    settings["openai_thread_id"] = "thread_2"

    thread_id = mocked_client._get_thread_id()
    assert thread_id == "thread_2"


def test_create_assistant(mocked_client, mocked_vector_store):
    mocked_client.vector_store = mocked_vector_store
    id = mocked_client._create_assistant()
    assert id == "assistant_vecsync-test_store_1"


def test_get_assistant_id_new(mocked_client, mocked_vector_store):
    mocked_client.vector_store = mocked_vector_store
    assistant_id = mocked_client._get_assistant_id()
    assert assistant_id == "assistant_vecsync-test_store_1"


def test_get_assistant_id_existing(mocked_client):
    mocked_client.client.beta.assistants.create(name="vecsync-1")
    assistant_id = mocked_client._get_assistant_id()
    assert assistant_id == "assistant_vecsync-1_1"


def test_get_assistant_id_multiple(mocked_client):
    mocked_client.client.beta.assistants.create(name="vecsync-1")
    mocked_client.client.beta.assistants.create(name="vecsync-2")
    assistant_id = mocked_client._get_assistant_id()
    assert assistant_id == "assistant_vecsync-1_1"
    assert len(mocked_client.client.beta.assistants.list()) == 1
