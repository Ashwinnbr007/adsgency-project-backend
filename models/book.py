from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from .review import Review

class CreateBook(BaseModel):
    title: str
    author: str
    genre: str
    published_date: date


class Book(BaseModel):
    bookId: int
    title: str
    author: str
    genre: str
    published_date: date
    review: Optional[List['Review']] = None
