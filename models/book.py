from typing import List
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator
from datetime import date
from .review import Review


class Book(BaseModel):
    title: str
    author: str
    genre: str
    published_date: date
    reviews: Optional[List[Review]] = []

    @validator("published_date", pre=True, always=True)
    def parse_published_date(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%d-%m-%Y")
            except ValueError:
                raise ValueError("Invalid date format. Please use dd-mm-yyyy.")
        return value
