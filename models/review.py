from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional


class Review(BaseModel):
    userId: str
    bookId: str

    rating: int = Field(None, ge=1, le=5)
    text: Optional[str] = None
    createdAt: Optional[datetime] = Field(default=datetime.utcnow())
