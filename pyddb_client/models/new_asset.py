from pydantic import BaseModel
import models


class NewAsset(BaseModel):
    asset_type: models.AssetType
    name: str
