from fastapi import APIRouter, Depends, HTTPException, status
from routers.models import User
from routers.auth import mongodb
from utils.auth_utils import *

api_router = APIRouter(
    prefix="/api",
    tags=["User Management"],
    responses={
        404: {"description": "Endpoint not found"},
        403: {"description": "Forbidden access"},
        200: {"description": "Success response"},
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized access"}
    }
)

@api_router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@api_router.get("/users/me/id")
async def get_me_id(current_user: User = Depends(get_current_active_user)):
    return await mongodb.get_me_id(current_user.username)

@api_router.get("/welcome/{username}")
async def welcome(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Welcome {current_user.username}!"}

@api_router.delete("/users/me")
async def delete_user(current_user: User = Depends(get_current_active_user)):
    await mongodb.delete_user(current_user.username)
    return {"message": "User deleted successfully"}

@api_router.put("/users/me/email", response_model=User)
async def update_user_email(email: str, current_user: User = Depends(get_current_active_user)):
    user_data = {
        "email": email,
        "disabled": False
    }

    if email == current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update email to the same value"
        )

    update_success = await mongodb.update_user(current_user.username, user_data)
    
    if not update_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )

    return User(username=current_user.username, email=email, disabled=False)

@api_router.put("/users/me/password", response_model=User)
async def update_user_password(password: str, current_user: User = Depends(get_current_active_user)):
    user_data = {
        "hashed_password": get_password_hash(password),
        "disabled": False
    }

    if password == current_user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update password to the same value"
        )

    update_success = await mongodb.update_user(current_user.username, user_data)
    
    if not update_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )

    return User(username=current_user.username, email=current_user.email, disabled=False)
