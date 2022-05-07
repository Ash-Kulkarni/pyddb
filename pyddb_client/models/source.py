from typing import Optional
from pydantic import BaseModel
import models


class Source(BaseModel):
    id: str
    name: Optional[str] = None
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    visible: Optional[bool] = None
    time: Optional[str] = None
    date_day: Optional[Optional[str]] = None
    date_month: Optional[Optional[str]] = None
    date_year: Optional[Optional[str]] = None
    reference: Optional[str] = None
    reference_id: Optional[str] = None
    reference_table: Optional[str] = None
    reference_url: Optional[str] = None
    scope: Optional[Optional[str]] = None
    title: Optional[str] = None
    url: Optional[Optional[str]] = None
    source_type: Optional[models.SourceType] = None

    def __repr__(self) -> str:
        return repr(f"Title: {self.title}, reference: {self.reference}, id: {self.id}")
