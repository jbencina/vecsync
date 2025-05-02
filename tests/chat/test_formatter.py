import pytest
from termcolor import colored

from vecsync.chat.formatter import ConsoleFormatter, GradioFormatter


@pytest.fixture
def console_formatter():
    return ConsoleFormatter()


@pytest.fixture
def gradio_formatter():
    return GradioFormatter()


def test_console_formatter_format_citation(console_formatter):
    citation_id = "123"
    expected = colored(f"[{citation_id}]", "yellow")
    assert console_formatter.format_citation(citation_id) == expected


def test_console_formatter_format_reference(console_formatter):
    citation_id = "123"
    file_name = "example.txt"
    expected = colored(f"\n[{citation_id}] {file_name}", "yellow")
    assert console_formatter.format_reference(citation_id, file_name) == expected


def test_console_formatter_get_references(console_formatter):
    annotations = {"file1": "123", "file2": "456"}
    files = {"file1": "example1.txt", "file2": "example2.txt"}
    expected = (
        "\n\nReferences\n----------\n"
        + colored("\n[123] example1.txt", "yellow")
        + colored("\n[456] example2.txt", "yellow")
    )
    assert console_formatter.get_references(annotations, files) == expected


def test_console_formatter_get_null_references(console_formatter):
    annotations = {}
    files = {}
    expected = ""
    assert console_formatter.get_references(annotations, files) == expected


def test_gradio_formatter_format_citation(gradio_formatter):
    citation_id = "123"
    expected = f"<strong>[{citation_id}]</strong>"
    assert gradio_formatter.format_citation(citation_id) == expected


def test_gradio_formatter_format_reference(gradio_formatter):
    citation_id = "123"
    file_name = "example.txt"
    expected = f"<strong>[{citation_id}]</strong> {file_name}"
    assert gradio_formatter.format_reference(citation_id, file_name) == expected


def test_gradio_formatter_get_references(gradio_formatter):
    annotations = {"file1": "123", "file2": "456"}
    files = {"file1": "example1.txt", "file2": "example2.txt"}
    expected = (
        "\n\nReferences\n----------\n" + "<strong>[123]</strong> example1.txt" + "<strong>[456]</strong> example2.txt"
    )
    assert gradio_formatter.get_references(annotations, files) == expected


def test_gradio_formatter_get_null_references(gradio_formatter):
    annotations = {}
    files = {}
    expected = ""
    assert gradio_formatter.get_references(annotations, files) == expected
