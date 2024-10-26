from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr
    disabled: bool = False

class UserCreate(UserBase):
    password: str

class User(UserBase):
    pass

class UserInDB(UserBase):
    hashed_password: str | None = None
    github_id: int | None = None
