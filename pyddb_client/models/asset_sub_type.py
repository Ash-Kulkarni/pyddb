from typing import Optional
from pydantic import BaseModel


class AssetSubType(BaseModel):
    id: str
    name: str
    parent_asset_sub_type_id: Optional[str]
