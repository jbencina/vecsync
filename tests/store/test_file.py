from pathlib import Path

import pytest

from vecsync.store.file import FileStore


@pytest.fixture
def temp_dir(tmp_path):
    # Create a temporary directory for testing
    pdf_file = tmp_path / "test.pdf"
    pdf_file.touch()
    non_pdf_file = tmp_path / "test.txt"
    non_pdf_file.touch()
    sub_dir = tmp_path / "subdir"
    sub_dir.mkdir()
    sub_pdf_file = sub_dir / "sub_test.pdf"
    sub_pdf_file.touch()
    return tmp_path


@pytest.fixture
def invalid_temp_dir(tmp_path):
    # Invalid path only has a non-PDF file
    non_pdf_file = tmp_path / "test.txt"
    non_pdf_file.touch()
    return tmp_path


def test_resolve_path():
    store = FileStore()
    assert store.path == Path.cwd()


def test_get_files(temp_dir):
    store = FileStore(path=temp_dir)
    files = store.get_files()
    expected_files = {temp_dir / "test.pdf", temp_dir / "subdir" / "sub_test.pdf"}
    assert set(files) == expected_files


def test_no_valid_files(invalid_temp_dir):
    store = FileStore(path=invalid_temp_dir)
    files = store.get_files()
    assert len(files) == 0
