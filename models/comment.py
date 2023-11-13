from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Comment(BaseModel):
    userId: str  # based on auth
    reviewId: str
    text: str
    createdAt: Optional[datetime] = Field(default=datetime.utcnow())
