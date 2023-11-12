from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from .comment import Comment


class Review(BaseModel):
    reviewId: int
    userId: int
    bookId: int

    rating: int = Field(None, ge=1, le=5)
    text: Optional[str] = None
    createdAt: Optional[datetime] = Field(default=datetime.utcnow())
