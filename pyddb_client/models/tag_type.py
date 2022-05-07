from typing import Optional
from pydantic import BaseModel


class TagType(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
