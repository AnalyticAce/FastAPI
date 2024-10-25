from authentication import (
    get_current_active_user, 
    authenticate_user,
    get_password_hash,
    create_access_token,
)
from authentication import app, mongodb, main
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from models import Token, User, UserCreate
from config import ACCESS_TOKEN_EXPIRE_MINUTES

@app.post("/token", response_model=Token, tags=["Access Management"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(mongodb, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register", response_model=User, tags=["Access Management"])
async def register_user(user: UserCreate):
    existing_user_by_username = await mongodb.get_user(user.username)
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_user_by_email = await mongodb.get_user_by_email(user.email)
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "disabled": False
    }
    
    result = await mongodb.create_user(user_data)
    return User(username=user.username, email=user.email, disabled=False)

@app.get("/users/me", response_model=User, tags=["User Management"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/welcome/{username}", tags=["User Management"])
async def welcome(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Welcome {current_user.username}!"}

@app.delete("/users/me", tags=["User Management"])
async def delete_user(current_user: User = Depends(get_current_active_user)):
    await mongodb.delete_user(current_user.username)
    return {"message": "User deleted successfully"}

@app.put("/users/me", response_model=User, tags=["User Management"])
async def update_user(user: UserCreate, current_user: User = Depends(get_current_active_user)):
    user_data = {
        "email": user.email,
        "disabled": False
    }

    if user.username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change username"
        )

    if user.password:
        hashed_password = get_password_hash(user.password)
        user_data["hashed_password"] = hashed_password

    update_success = await mongodb.update_user(current_user.username, user_data)
    
    if not update_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )

    return User(username=current_user.username, email=user.email, disabled=False)
