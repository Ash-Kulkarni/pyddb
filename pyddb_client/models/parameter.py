from typing import Optional, List
from pydantic import BaseModel
import pyddb_client.models as models


class Parameter(BaseModel):
    id: str
    created_at: str
    project_id: str
    created_by: str
    parameter_type: models.ParameterType
    parents: Optional[List[models.Asset]]
    revision: Optional[models.Revision]
    deleted_at: Optional[str]
