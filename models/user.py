from pydantic import BaseModel


class User(BaseModel):
    userId: int
    username: str
    email: str
    password: str
    role: str