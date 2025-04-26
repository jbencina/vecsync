import builtins
import sqlite3
import pytest
from pathlib import Path

# Adjust this import to match where you defined ZoteroStore & Collection
from vecsync.store.zotero import ZoteroStore, Collection
from vecsync.settings import SettingExists


def test_resolve_path_existing(monkeypatch, settings_mock):
    monkeypatch.setattr(
        "vecsync.store.zotero.Settings",
        lambda: settings_mock({"zotero_path": "/Users/alice/Zotero"}),
    )
    path = ZoteroStore._resolve_path()
    assert str(path) == "/Users/alice/Zotero"


def test_resolve_path_missing_default(monkeypatch, settings_mock):
    settings = settings_mock({})
    monkeypatch.setattr("vecsync.store.zotero.Settings", lambda: settings)
    monkeypatch.setattr("vecsync.store.zotero.getuser", lambda: "bob")
    monkeypatch.setattr(builtins, "input", lambda prompt="": "")

    path = ZoteroStore._resolve_path()
    assert str(path) == "/Users/bob/Zotero"
    assert settings["zotero_path"].value == "/Users/bob/Zotero"
    assert type(settings["zotero_path"]) is SettingExists


def test_resolve_path_missing_prompt(monkeypatch, settings_mock):
    settings = settings_mock({})
    monkeypatch.setattr("vecsync.store.zotero.Settings", lambda: settings)
    monkeypatch.setattr(builtins, "input", lambda prompt="": "/Users/carol/Zotero")

    path = ZoteroStore._resolve_path()
    assert str(path) == "/Users/carol/Zotero"
    assert settings["zotero_path"].value == "/Users/carol/Zotero"
    assert type(settings["zotero_path"]) is SettingExists


def test_get_collections(zotero_db_mock):
    db = sqlite3.connect(zotero_db_mock)
    store = ZoteroStore(db_connection=db, root=Path(""))
    cols = store.get_collections()

    assert isinstance(cols, list)
    assert [(c.id, c.name) for c in cols] == [(1, "Foo"), (2, "Bar")]


def test_resolve_collection_existing(monkeypatch, settings_mock):
    settings = settings_mock({"zotero_collection": 123})
    monkeypatch.setattr("vecsync.store.zotero.Settings", lambda: settings)

    collection = ZoteroStore._resolve_collection([])
    assert collection == 123


def test_resolve_collection_prompt_success(monkeypatch, settings_mock):
    settings = settings_mock({})
    monkeypatch.setattr("vecsync.store.zotero.Settings", lambda: settings)
    monkeypatch.setattr(builtins, "input", lambda prompt="": "123")

    collection = ZoteroStore._resolve_collection([Collection(id=123, name="Test")])
    assert collection == 123


def test_resolve_collection_prompt_fail(monkeypatch, settings_mock):
    settings = settings_mock({})
    monkeypatch.setattr("vecsync.store.zotero.Settings", lambda: settings)
    monkeypatch.setattr(builtins, "input", lambda prompt="": "456")

    # Assert index error is raised
    with pytest.raises(IndexError):
        ZoteroStore._resolve_collection([Collection(id=123, name="Test")])


def test_resolve_collection_prompt_blank(monkeypatch, settings_mock):
    settings = settings_mock({})
    monkeypatch.setattr("vecsync.store.zotero.Settings", lambda: settings)
    monkeypatch.setattr(builtins, "input", lambda prompt="": "")

    collection = ZoteroStore._resolve_collection([Collection(id=123, name="Test")])
    assert collection == 123
