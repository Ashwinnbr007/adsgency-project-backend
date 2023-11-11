from pydantic import BaseModel

class CreateUser(BaseModel):
    username: str
    email: str
    password: str
    role: str = 'user'

class User(BaseModel):
    userId: int
    username: str
    email: str
    password:str
    role: str
    
class Token(BaseModel):
    access_token: str
    token_type: str