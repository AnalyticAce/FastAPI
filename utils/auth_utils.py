from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from routers.models import TokenData, UserInDB, User
from utils.config import (
    SECRET_KEY, ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    MONGO_DB_NAME, MONGO_COLLECTION_NAME_USER
)
from db.mongo import Mongo

mongodb = Mongo(MONGO_DB_NAME, MONGO_COLLECTION_NAME_USER)

async def main():
    await mongodb.create_db(MONGO_DB_NAME)
    await mongodb.create_collection(MONGO_COLLECTION_NAME_USER)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_context.hash(password)

async def authenticate_user(db, username: str, password: str):
    user = await mongodb.get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithm=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
                                    status_code=status.HTTP_401_UNAUTHORIZED, 
                                    detail="Could not validate credentials", 
                                    headers={"WWW-Authenticate": "Bearer"}
                                )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await mongodb.get_user(username=token_data.username)
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Invalid user")

    return current_user