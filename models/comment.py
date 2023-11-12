from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Comment(BaseModel):
    userId: str  # based on auth
    text: str
    createdAt: Optional[datetime] = Field(default=datetime.utcnow())
