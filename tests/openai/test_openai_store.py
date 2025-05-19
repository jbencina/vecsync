import pytest


def test_get_files_none(mocked_vector_store):
    files = mocked_vector_store.get_files()
    assert len(files) == 0


def test_get_valid_store(mocked_vector_store):
    store = mocked_vector_store.get()
    assert store.name == "test_store"
    assert store.id == "vector_store_1"


def test_get_invalid_store(mocked_vector_store):
    mocked_vector_store.name = "invalid_store"
    with pytest.raises(ValueError):
        mocked_vector_store.get()


def test_get_files_empty(mocked_vector_store):
    mocked_vector_store.get()
    files = mocked_vector_store.get_files()
    assert len(files) == 0


def test_get_files_existing(mocked_vector_store, create_test_upload):
    files_uploaded = mocked_vector_store._upload_files(create_test_upload)

    remote_files = mocked_vector_store.get_files()

    assert len(remote_files) == len(files_uploaded) == 3


def test_delete_files(mocked_vector_store, create_test_upload):
    files_uploaded = mocked_vector_store._upload_files(create_test_upload)
    assert len(files_uploaded) == 3

    removed_files = mocked_vector_store._delete_files(files_uploaded)
    assert len(removed_files) == 3

    remote_files = mocked_vector_store.get_files()
    assert len(remote_files) == 0


def test_delete_files_invalid(mocked_vector_store):
    removed_files = mocked_vector_store._delete_files(["test"])
    assert len(removed_files) == 0

    remote_files = mocked_vector_store.get_files()
    assert len(remote_files) == 0


def test_delete_store(mocked_vector_store):
    mocked_vector_store.delete()
    assert mocked_vector_store.store is None


def test_get(mocked_vector_store):
    store = mocked_vector_store.get()
    assert store.name == "test_store"
    assert store.id == "vector_store_1"


def test_attach_files(mocked_vector_store, create_test_upload):
    files_uploaded = mocked_vector_store._upload_files(create_test_upload)
    assert len(files_uploaded) == 3

    mocked_vector_store._attach_files(files_uploaded)

    remote_files = mocked_vector_store.get_files()
    assert len(remote_files) == 3


def test_sync_files(mocked_vector_store, create_test_upload):
    result = mocked_vector_store.sync(create_test_upload)

    assert result.files_saved == 3
    assert result.files_deleted == 0
    assert result.files_skipped == 0
    assert result.remote_count == 3
    assert result.duration > 0


def test_sync_files_with_existing_overlap(mocked_vector_store, create_test_upload):
    files = list(create_test_upload)

    result1 = mocked_vector_store.sync(files[:2])
    assert result1.files_saved == 2

    result2 = mocked_vector_store.sync(files)
    assert result2.files_saved == 1
    assert result2.files_deleted == 0
    assert result2.files_skipped == 2
    assert result2.remote_count == 3
    assert result2.duration > 0
