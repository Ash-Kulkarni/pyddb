from typing import Optional
from pydantic import BaseModel


class SourceType(BaseModel):
    id: str
    name: str
    visible: bool
    deleted_at: Optional[str]

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, id: {self.id}")
