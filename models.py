from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class LogoutResponse(BaseModel):
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str | None] = None

class User(BaseModel):
    username: str = Field(..., example="johndoe")
    email: EmailStr = Field(..., example="johndoe@gmail.com")
    disabled: Optional[bool | None] = None

class UserCreate(BaseModel):
    username: str
    email: str
    hashed_password: str
    disabled: Optional[bool | None] = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
