from typing import Optional
from pydantic import BaseModel
import pyddb_client.models as models


class ItemType(BaseModel):
    id: str
    created_at: Optional[str]
    updated_at: Optional[str]
    deleted_at: Optional[str]
    parameter_type: models.ParameterType
    asset_type: Optional[models.AssetType]
    created_by: models.Staff
    updated_by: models.Staff
