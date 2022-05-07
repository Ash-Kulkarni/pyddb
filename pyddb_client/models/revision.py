from typing import Optional, List
from pydantic import BaseModel
import pyddb_client.models as models


class Revision(BaseModel):
    id: str
    status: str
    source: models.Source
    comment: Optional[str]
    location_in_source: Optional[str]
    values: List[models.Value]
    created_at: str
    created_by: models.Staff

    def __repr__(self) -> str:
        return repr(
            f"Value: {self.values}, Created by: {self.created_by.staff_name}, Status: {self.status}, Source: {self.source.title} - {self.source.reference}"
        )
