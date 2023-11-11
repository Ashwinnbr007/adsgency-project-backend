from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Comment(BaseModel):
    userId: int
    commentId: int
    reviewId: Optional[int] = None
    bookId: int

    text: str
    createdAt: Optional[datetime] = Field(default=datetime.utcnow())
