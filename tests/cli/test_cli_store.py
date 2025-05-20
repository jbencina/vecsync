from click.testing import CliRunner

import vecsync.cli.store as cli


def test_list_stores_empty(monkeypatch, mocked_vector_store):
    monkeypatch.setattr("vecsync.cli.store.OpenAiVectorStore", lambda _: mocked_vector_store)

    runner = CliRunner()
    result = runner.invoke(cli.list_stores)
    assert result.exit_code == 0

    assert "0 Files in store 'test_store':" in result.output


def test_list_stores_non_empty(monkeypatch, mocked_vector_store, tmp_path):
    filename = tmp_path / "data.pdf"
    with open(filename, "w") as f:
        f.write("Test data")

    mocked_vector_store._upload_files({filename})
    monkeypatch.setattr("vecsync.cli.store.OpenAiVectorStore", lambda _: mocked_vector_store)

    runner = CliRunner()
    result = runner.invoke(cli.list_stores)
    assert result.exit_code == 0

    assert "1 Files in store 'test_store':" in result.output
    assert "data.pdf" in result.output


def test_delete_stores(monkeypatch, mocked_vector_store, tmp_path):
    filename = tmp_path / "data.pdf"
    with open(filename, "w") as f:
        f.write("Test data")

    mocked_vector_store._upload_files({filename})
    monkeypatch.setattr("vecsync.cli.store.OpenAiVectorStore", lambda _: mocked_vector_store)

    runner = CliRunner()
    result = runner.invoke(cli.delete)
    assert result.exit_code == 0

    assert "Deleting 1 files from" in result.output
    assert "Deleting vector store" in result.output
