import json

from vecsync.settings import SettingExists, SettingMissing, Settings


def test_write_settings(tmp_path):
    settings = Settings(path=tmp_path / "settings.json")

    settings["test"] = "value"
    settings["test2"] = {"k": "v"}

    with open(tmp_path / "settings.json") as f:
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


def test_delete_settings(settings_fixture):
    settings = Settings(path=settings_fixture)
    del settings["test"]

    with open(settings_fixture) as f:
        data = json.load(f)

    assert "test" not in data
    assert len(data) == 0


def test_delete_settings_missing(settings_fixture):
    settings = Settings(path=settings_fixture)
    del settings["doesNotExist"]
    # No exception should be raised
