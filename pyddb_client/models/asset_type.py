from typing import Optional
from . import AssetTypeGroup
from pydantic import BaseModel


class AssetType(BaseModel):
    id: str
    name: str
    created_at: Optional[str]
    updated_at: Optional[str]
    asset_sub_type: Optional[bool]
    deleted_at: Optional[str]
    asset_type_group: Optional[AssetTypeGroup]
    parent_id: Optional[str]

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, id: {self.id}")
