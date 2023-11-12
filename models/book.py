from pydantic import BaseModel
from datetime import date


class Book(BaseModel):
    bookId: int
    title: str
    author: str
    genre: str
    published_date: date
