from vecsync.settings import Settings, SettingExists, SettingMissing
import json


def test_write_settings(tmp_path):
    settings = Settings(path=tmp_path / "settings.json")

    settings["test"] = "value"
    settings["test2"] = {"k": "v"}

    with open(tmp_path / "settings.json", "r") as f:
        data = json.load(f)

    assert data["test"] == "value"
    assert data["test2"]["k"] == "v"
    assert len(data) == 2


def test_read_settings(settings_fixture):
    settings = Settings(path=settings_fixture)
    assert type(settings["test"]) is SettingExists
    assert settings["test"].value == "value"


def test_read_missing_setting(settings_fixture):
    settings = Settings(path=settings_fixture)
    assert type(settings["missing"]) is SettingMissing
