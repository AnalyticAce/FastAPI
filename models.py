from pydantic import BaseModel
from typing import Optional

class LogoutResponse(BaseModel):
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str | None] = None

class User(BaseModel):
    username: str
    email: Optional[str | None] = None
    full_name: Optional[str | None] = None
    disabled: Optional[bool | None] = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
