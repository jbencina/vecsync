from click.testing import CliRunner

import vecsync.cli.sync as cli


def test_sync_filesource(monkeypatch, tmp_path, mocked_vector_store):
    filename = tmp_path / "data.pdf"

    with open(filename, "w") as f:
        f.write("Test data")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("vecsync.cli.sync.OpenAiVectorStore", lambda _: mocked_vector_store)

    runner = CliRunner()
    result = runner.invoke(cli.sync, ["--source", "file"])
    assert result.exit_code == 0

    assert "Syncing 1 files from local to OpenAI" in result.output
    assert "Saved: 1 | Deleted: 0 | Skipped: 0" in result.output

    assert len(mocked_vector_store.get_files()) == 1
