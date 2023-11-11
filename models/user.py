from pydantic import BaseModel

class CreateUser(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str
    role: str = 'user'
    
class Token(BaseModel):
    access_token: str
    token_type: str