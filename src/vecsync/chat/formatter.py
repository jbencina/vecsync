from abc import ABC, abstractmethod

from termcolor import colored


class BaseFormatter(ABC):
    @abstractmethod
    def format_citation(self, citation_id: str) -> str:
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def format_reference(self, citation_id: str, file_name: str) -> str:
        raise NotImplementedError("Subclasses must implement this method")

    def get_references(self, annotations: dict[str, str], files: dict[str, str]) -> str:
        if len(annotations) == 0:
            return ""

        text_chunks = []
        text_chunks.append("\n")
        text_chunks.append("\nReferences")
        text_chunks.append("\n----------\n")

        for file_id, citation_id in annotations.items():
            text_chunks.append(self.format_reference(citation_id, files[file_id]))

        return "".join(text_chunks)


class ConsoleFormatter(BaseFormatter):
    def format_citation(self, citation_id: str) -> str:
        return colored(f"[{citation_id}]", "yellow")

    def format_reference(self, citation_id: str, file_name: str) -> str:
        return colored(f"\n[{citation_id}] {file_name}", "yellow")


class GradioFormatter(BaseFormatter):
    def format_citation(self, citation_id: str) -> str:
        return f"<strong>[{citation_id}]</strong>"

    def format_reference(self, citation_id: str, file_name: str) -> str:
        return f"<strong>[{citation_id}]</strong> {file_name}"
