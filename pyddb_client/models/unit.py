from typing import Optional
from pydantic import BaseModel


class Unit(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    unit_type_id: Optional[str]
    unit_system_id: Optional[str]
