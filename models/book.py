from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class CreateBook(BaseModel):
    title: str
    author: str
    genre: str
    published_date: date

class Comment(BaseModel):
    user: str
    userId: int
    text: str
    replies: Optional[List['Comment']] = []

class Review(BaseModel):
    userId: int
    rating: int = Field(None, ge=1, le=5)
    text: str
    

class Book(BaseModel):
    bookId: int
    title: str
    author: str
    genre: str
    published_date: date
    review: Optional[Review] = None
    comments: Optional[List[Comment]] = []