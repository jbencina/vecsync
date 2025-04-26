from pytest import fixture
from vecsync.settings import Settings, SettingExists, SettingMissing
import sqlite3


@fixture(scope="session")
def settings_fixture(tmp_path_factory):
    path = tmp_path_factory.mktemp("settings") / "settings.json"
    settings = Settings(path=path)
    settings["test"] = "value"
    return path


class MockSettings:
    """
    A minimal stand-in for Settings() so we can control
    which keys exist or are missing, and inspect writes.
    """

    def __init__(self, vals):
        self.vals = vals

    def __getitem__(self, key):
        if key in self.vals:
            return SettingExists(key=key, value=self.vals[key])
        return SettingMissing(key=key)

    def __setitem__(self, key, value):
        self.vals[key] = value


@fixture(scope="session")
def settings_mock():
    return MockSettings


@fixture(scope="session")
def zotero_db_mock(tmp_path_factory):
    # Prepare a fake DB
    dbfile = tmp_path_factory.mktemp("db") / "zotero.sqlite"
    conn = sqlite3.connect(str(dbfile))
    cur = conn.cursor()
    cur.execute("CREATE TABLE collections (collectionID INTEGER, collectionName TEXT)")
    cur.executemany("INSERT INTO collections VALUES (?,?)", [(1, "Foo"), (2, "Bar")])
    conn.commit()
    conn.close()

    return dbfile
