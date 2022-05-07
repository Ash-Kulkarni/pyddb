from pydantic import BaseModel
import pyddb_client.models as models


class NewAsset(BaseModel):
    asset_type: models.AssetType
    name: str
