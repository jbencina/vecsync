from openai import OpenAI
from pathlib import Path
from pydantic import BaseModel
from tqdm import tqdm
from termcolor import cprint
from time import perf_counter


class SyncOperationResult(BaseModel):
    files_saved: int
    files_deleted: int
    files_skipped: int
    updated_count: int
    duration: float


class OpenAiVectorStore:
    def __init__(self, name: str):
        self.client = OpenAI()
        self.name = name
        self.store = None

    def create(self):
        self.store = self.client.vector_stores.create(name=self.name)
        return self.store

    def get(self):
        stores = self.client.vector_stores.list()

        for store in stores:
            if store.name == self.name:
                self.store = store
                return store

        raise ValueError(f"Vector store with name {self.name} not found.")

    def get_files(self):
        files = self.client.files.list()
        return [file.filename for file in files]

    def get_or_create(self):
        try:
            return self.get()
        except ValueError:
            return self.create()

    def delete(self):
        if not self.store:
            self.get()

        remote_files = self.client.files.list()
        self._delete_files([f.id for f in remote_files])

        cprint(f"👋 Deleting vector store {self.store.name}", "red")
        self.client.vector_stores.delete(vector_store_id=self.store.id)
        self.store = None

    def _attach_files(self, files_to_attach: set[str]):
        cprint(f"Attaching {len(files_to_attach)} files to OpenAI vector store", "blue")
        for file in tqdm(files_to_attach):
            self.client.vector_stores.files.create_and_poll(
                vector_store_id=self.store.id,
                file_id=file,
            )

    def _delete_files(self, files_to_remove: list[str]) -> set[str]:
        cprint(
            f"👋 Deleting {len(files_to_remove)} files from OpenAI file storage", "red"
        )

        removed_file_ids = []
        for file_id in tqdm(files_to_remove):
            self.client.vector_stores.files.delete(
                vector_store_id=self.store.id, file_id=file_id
            )
            self.client.files.delete(file_id=file_id)
            removed_file_ids.append(file_id)

        return set(removed_file_ids)

    def _upload_files(self, files_to_upload: set[Path]) -> set[str]:
        cprint(f"Uploading {len(files_to_upload)} files to OpenAI file storage", "blue")

        uploaded_file_ids = []
        for file in tqdm(files_to_upload):
            with open(file, "rb") as f:
                file_object = self.client.files.create(file=f, purpose="assistants")
                uploaded_file_ids.append(file_object.id)

        return set(uploaded_file_ids)

    def sync(self, files: list[Path]):
        ts_start = perf_counter()
        if not self.store:
            self.get_or_create()

        incoming_file_names = set([f.name for f in files])

        # Check file storage
        remote_files = self.client.files.list()
        remote_file_ids = set([f.id for f in remote_files])
        remote_file_names = set([f.filename for f in remote_files])

        # Determine missing files
        duplicate_file_names = remote_file_names & incoming_file_names
        new_file_names = incoming_file_names - remote_file_names
        extra_file_names = remote_file_names - incoming_file_names

        files_to_upload = [f for f in files if f.name in new_file_names]
        files_to_remove = [f.id for f in remote_files if f.filename in extra_file_names]

        if len(files_to_upload) > 0:
            remote_file_ids.update(self._upload_files(files_to_upload))

        if len(files_to_remove) > 0:
            remote_file_ids.difference_update(self._delete_files(files_to_remove))

        # Check vector storage
        existing_vector_files = self.client.vector_stores.files.list(
            vector_store_id=self.store.id
        )
        existing_vector_file_ids = set([f.id for f in existing_vector_files])

        # Determine missing files
        files_to_attach = remote_file_ids - existing_vector_file_ids

        if len(files_to_attach) > 0:
            self._attach_files(files_to_attach)

        ts_end = perf_counter()
        duration = ts_end - ts_start

        return SyncOperationResult(
            files_saved=len(files_to_upload),
            files_deleted=len(files_to_remove),
            files_skipped=len(duplicate_file_names),
            updated_count=len(existing_vector_file_ids | files_to_attach),
            duration=duration,
        )
