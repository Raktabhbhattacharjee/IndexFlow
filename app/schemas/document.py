from pydantic import BaseModel
from app.models.document import IndexingStatus
from datetime import datetime


class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    indexing_status: IndexingStatus
    created_at: datetime

    class Config:
        from_attributes = True
