from typing import Optional
from pydantic import BaseModel


class UnitSystem(BaseModel):
    id: str
    name: str
    short_name: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
