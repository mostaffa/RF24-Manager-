# app/schemas/auth.py
from app.schemas.user import UserRead
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None  
class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    user: UserRead
    class Config:
        from_attributes = True
