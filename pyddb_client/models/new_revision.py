from typing import Union, Optional
from pydantic import BaseModel
import pyddb_client.models as models


class NewRevision(BaseModel):

    value: Union[str, int, float, bool]
    unit: Optional[models.Unit]
    source: Union[models.Source, models.NewSource]
    comment: str = "Empty"
    location_in_source: str = "Empty"
