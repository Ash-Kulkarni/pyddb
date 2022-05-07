from typing import Optional
from pydantic import BaseModel
import pyddb_client.models as models


class NewParameter(BaseModel):
    id: Optional[str]
    parameter_type: models.ParameterType
    revision: Optional[models.NewRevision]
