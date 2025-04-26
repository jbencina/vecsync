import sqlite3
from pydantic import BaseModel
from pathlib import Path
from vecsync.settings import Settings, SettingExists, SettingMissing
from getpass import getuser
from termcolor import cprint


class Collection(BaseModel):
    id: int
    name: str


class ZoteroStore:
    def __init__(
        self,
        root: Path,
        db_connection: sqlite3.Connection,
    ):
        self.root = root
        self.db = db_connection

    @classmethod
    def client(cls):
        """Prompt the user for path & collection, then return a ready-to-use instance."""
        root = Path(cls._resolve_path())
        db = sqlite3.connect(root / "zotero.sqlite")
        store = cls(root=root, db_connection=db)
        return store

    @staticmethod
    def _resolve_path() -> Path:
        settings = Settings()

        match settings["zotero_path"]:
            case SettingMissing():
                # TODO: Make this portable across OSes
                default_path = Path(f"/Users/{getuser()}/Zotero")
                zotero_path = input(
                    f"Enter the path to your Zotero directory (Default: {default_path}): "
                )

                if zotero_path.strip() == "":
                    zotero_path = default_path

                settings["zotero_path"] = str(zotero_path)
            case SettingExists() as x:
                zotero_path = Path(x.value)

        return zotero_path

    @staticmethod
    def _resolve_collection(collections: list[Collection]) -> int:
        settings = Settings()

        match settings["zotero_collection"]:
            case SettingMissing():
                cprint("Available collections:", "blue")
                for collection in collections:
                    print(f"[{collection.id}]: {collection.name}")

                default_collection = collections[0].id
                zotero_collection = input(
                    f"Enter the collection ID to sync (Default: {default_collection}): "
                )

                if zotero_collection.strip() == "":
                    zotero_collection = default_collection
                else:
                    zotero_collection = int(zotero_collection)
                    if zotero_collection not in [c.id for c in collections]:
                        raise IndexError("Invalid collection ID.")

                settings["zotero_collection"] = zotero_collection
            case SettingExists() as x:
                zotero_collection = int(x.value)

        return zotero_collection

    def get_collections(self):
        """
        Get all collections from the Zotero database.
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT
                collectionID,
                collectionName
            FROM collections
        """)
        rows = cursor.fetchall()
        collections = []
        for row in rows:
            collection = Collection(id=row[0], name=row[1])
            collections.append(collection)
        return collections

    def get_files(self):
        """
        Get all files from the Zotero database.
        """
        collections = self.get_collections()
        collection_id = self._resolve_collection(collections)

        cursor = self.db.cursor()
        cursor.execute(
            """
            SELECT
                i.key,
                a.path
            FROM collectionItems ci
            INNER JOIN itemAttachments a ON ci.itemID = a.parentItemID
            INNER JOIN items i ON a.itemID = i.itemID
            WHERE
                ci.collectionID = ?
                AND a.contentType = 'application/pdf'
        """,
            (collection_id,),
        )
        rows = cursor.fetchall()
        files = []
        for row in rows:
            key = row[0]
            filename = row[1].replace("storage:", "")
            files.append(self.root / "storage" / key / filename)
        return files
