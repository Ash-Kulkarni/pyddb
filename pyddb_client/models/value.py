from typing import Optional, Union
from pydantic import BaseModel
import pyddb_client.models as models


class Value(BaseModel):
    id: Optional[str]
    value: Union[float, str, bool, None]
    unit: Optional[models.Unit]
