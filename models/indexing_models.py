from pydantic import BaseModel

class FolderInput(BaseModel):
    folder: str
