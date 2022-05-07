from typing import Optional, List
from pydantic import BaseModel
import models


class ParameterType(BaseModel):
    id: str
    name: str
    data_type: str
    created_at: Optional[str]
    updated_at: Optional[str]
    global_parameter: bool
    deleted_at: Optional[str]
    default_unit: Optional[models.Unit]
    units: Optional[List[models.Unit]]
    unit_type: Optional[models.UnitType]

    def __repr__(self) -> str:
        return repr("Name: " + self.name + ", Data type: " + self.data_type)
