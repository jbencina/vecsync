from click.testing import CliRunner

import vecsync.cli.settings as cli
from vecsync.settings import Settings


def test_settings_show(monkeypatch, tmp_path):
    # Mock the Settings class and its methods
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr("vecsync.cli.settings.Settings", lambda: Settings(settings_file))

    runner = CliRunner()
    result = runner.invoke(cli.show)
    assert result.exit_code == 0
    assert f"Settings file location: {settings_file}" in result.output
    assert "Settings file data:" in result.output


def test_settings_delete(monkeypatch, tmp_path):
    # Mock the Settings class and its methods
    settings_file = tmp_path / "settings.json"
    settings = Settings(settings_file)
    settings["key"] = "value"

    monkeypatch.setattr("vecsync.cli.settings.Settings", lambda: Settings(settings_file))

    runner = CliRunner()
    result = runner.invoke(cli.clear)

    assert result.exit_code == 0
    assert "Settings file cleared." in result.output
    assert not settings_file.exists()
