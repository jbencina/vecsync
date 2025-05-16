from pydantic import BaseModel


class Assistant(BaseModel):
    id: str
    name: str
