from pathlib import Path


class FileStore:
    def __init__(self, path: Path | None = None):
        self.path = path or self._resolve_path()

    @staticmethod
    def _resolve_path() -> Path:
        # Get the current directory of the terminal
        return Path.cwd()

    def get_files(self) -> list[Path]:
        files = []
        for file in self.path.rglob("*.pdf"):
            if file.is_file():
                files.append(file)
        return files
