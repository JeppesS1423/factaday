from datetime import datetime
from pydantic import BaseModel

from .enums import FactCategory


class FactCreate(BaseModel):
    content: str
    category: FactCategory

class FactResponse(BaseModel):
    id: int
    content: str
    category: FactCategory
    created_at: datetime

    class Config:
        from_attributes = True
