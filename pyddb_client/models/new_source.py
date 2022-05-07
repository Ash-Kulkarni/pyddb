from typing import Optional
from pydantic import BaseModel
import pyddb_client.models as models


class NewSource(BaseModel):
    source_type: models.SourceType
    title: str
    reference: str
    url: Optional[str]
    day: Optional[int]
    month: int = 1
    year: int = 2001
