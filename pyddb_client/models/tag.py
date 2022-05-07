from typing import Optional
from pydantic import BaseModel
import pyddb_client.models as models


class Tag(BaseModel):
    id: str
    name: str
    global_tag: bool
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    tag_type: models.TagType
