# pragma: exclude file

from pydantic import BaseModel


class StoredFile(BaseModel):
    id: str
    name: str
