from vecsync.settings import Settings


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


def test_load_history_none(mocked_client):
    history = mocked_client.load_history()
    assert history == []


def test_load_history_valid(mocked_client):
    mocked_client.send_message("Hello")
    mocked_client.send_message("World")
    mocked_client.client.beta.threads.messages.create(
        thread_id=mocked_client.thread_id, role="assistant", content="Response"
    )

    history = mocked_client.load_history()

    assert len(history) == 3
    assert [x["role"] for x in history] == ["user", "user", "assistant"]


def test_message(mocked_client, mocked_client_handler):
    mocked_client.stream_response(thread_id="", assistant_id="", handler=mocked_client_handler)

    items = []
    while not mocked_client_handler.queue.empty():
        items.append(mocked_client_handler.queue.get_nowait())

    assert items == ["This", "is", "a", "test", "message", "from", "the", "assistant"]


def test_consume_queue(mocked_client, mocked_client_handler):
    mocked_client.stream_response(thread_id="", assistant_id="", handler=mocked_client_handler)

    items = list(mocked_client_handler.consume_queue())

    assert items == ["This", "is", "a", "test", "message", "from", "the", "assistant"]
