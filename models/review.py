from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from .comment import Comment


class Review(BaseModel):
    userId: str

    rating: int = Field(None, ge=1, le=5)
    comments: Optional[List[Comment]] = []
    text: Optional[str] = None
    createdAt: Optional[datetime] = Field(default=datetime.utcnow())
