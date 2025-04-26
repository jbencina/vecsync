from appdirs import user_config_dir
from pathlib import Path
import json
from pydantic import BaseModel
from typing import Any


class SettingExists(BaseModel):
    key: str
    value: Any


class SettingMissing(BaseModel):
    key: str


class Settings:
    def __init__(self, path: str | None = None):
        self.file = path or Path(user_config_dir("vecsync")) / "settings.json"

        if not self.file.exists():
            self.create()

    def create(self):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file, "w") as f:
            json.dump({}, f)  # initialize empty JSON

    def delete(self):
        if self.file.exists():
            self.file.unlink()

    def __getitem__(self, key: str) -> SettingExists | SettingMissing:
        with open(self.file, "r") as f:
            data = json.load(f)
            result = data.get(key, None)

        if result is None:
            return SettingMissing(key=key)
        else:
            return SettingExists(key=key, value=result)

    def __setitem__(self, key: str, value: str):
        with open(self.file, "r") as f:
            data = json.load(f)
            data[key] = value

        with open(self.file, "w") as f:
            json.dump(data, f)
