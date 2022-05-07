from pydantic import BaseModel


class UnitType(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
