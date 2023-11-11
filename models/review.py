from pydantic import BaseModel, Field
from typing import List, Optional
from .comment import Comment

class Review(BaseModel):
    userId: int
    bookId: int
    rating: int = Field(None, ge=1, le=5)
    text: str
    replies: Optional[List[Comment]] = None