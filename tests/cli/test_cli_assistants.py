from click.testing import CliRunner

import vecsync.cli.assistants as cli


def test_list_assistants_empty(monkeypatch, mocked_client):
    monkeypatch.setattr("vecsync.cli.assistants.OpenAIClient", lambda store_name: mocked_client)

    runner = CliRunner()
    result = runner.invoke(cli.list_assistants)
    assert result.exit_code == 0

    assert "No assistants found." in result.output


def test_list_assistants_non_empty(monkeypatch, mocked_client):
    mocked_client.client.beta.assistants.create(name="vecsync-1")
    mocked_client.client.beta.assistants.create(name="other-1")
    monkeypatch.setattr("vecsync.cli.assistants.OpenAIClient", lambda store_name: mocked_client)

    runner = CliRunner()
    result = runner.invoke(cli.list_assistants)
    assert result.exit_code == 0

    assert "Assistants in your OpenAI account:" in result.output
    assert "vecsync-1" in result.output
    assert "other-1" not in result.output


def test_clean_assistants_empty(monkeypatch, mocked_client):
    monkeypatch.setattr("vecsync.cli.assistants.OpenAIClient", lambda store_name: mocked_client)

    runner = CliRunner()
    result = runner.invoke(cli.clean)
    assert result.exit_code == 0

    assert "No deletable assistants found." in result.output


def test_clean_assistants_non_empty(monkeypatch, mocked_client):
    mocked_client.client.beta.assistants.create(name="vecsync-1")
    monkeypatch.setattr("vecsync.cli.assistants.OpenAIClient", lambda store_name: mocked_client)

    runner = CliRunner()
    result = runner.invoke(cli.clean, input="y\n")
    assert result.exit_code == 0

    assert "Deleting assistant vecsync-1" in result.output


def test_clean_assistants_abort(monkeypatch, mocked_client):
    mocked_client.client.beta.assistants.create(name="vecsync-1")
    monkeypatch.setattr("vecsync.cli.assistants.OpenAIClient", lambda store_name: mocked_client)

    runner = CliRunner()
    result = runner.invoke(cli.clean, input="n\n")
    assert result.exit_code == 0

    assert "Aborting" in result.output


def test_clean_assistants_invalid(monkeypatch, mocked_client):
    mocked_client.client.beta.assistants.create(name="vecsync-1")
    monkeypatch.setattr("vecsync.cli.assistants.OpenAIClient", lambda store_name: mocked_client)

    runner = CliRunner()
    result = runner.invoke(cli.clean, input="f\n")
    assert result.exit_code == 1

    assert "Please enter" in result.output
