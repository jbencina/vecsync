# pragma: exclude file

from enum import Enum

from pydantic import BaseModel


class FileStatus(str, Enum):
    ATTACHED = "attached"
    DETACHED = "detached"


class StoredFile(BaseModel):
    id: str
    name: str
    status: FileStatus
