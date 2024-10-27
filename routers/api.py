from fastapi import APIRouter, Depends, HTTPException, Request, status
from routers.models import User
from routers.auth import mongodb
from utils.auth_utils import *
from routers.limiter import limiter

api_router = APIRouter(
    prefix="/api/v1",
    tags=["User Management"],
    responses={
        404: {"description": "Endpoint not found"},
        403: {"description": "Forbidden access"},
        200: {"description": "Success response"},
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized access"}
    }
)

@api_router.get(
    "/users/me",
    response_model=User,
    summary="Get Current User",
    description="Retrieves the currently authenticated user's profile information.",
    response_description="Returns the current user's profile data including username, email, and disabled status."
)
@limiter.limit('5/second')
async def read_users_me(
    request: Request,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Fetch details of the currently authenticated user.

    Args:
        request (Request): The incoming request object
        current_user (User): The current authenticated user, injected by dependency

    Returns:
        User: The current user's profile information

    Rate Limit:
        5 requests per second
    """
    return current_user

@api_router.get(
    "/users/me/id",
    summary="Get User ID",
    description="Retrieves the unique identifier for the currently authenticated user.",
    response_description="Returns the user's unique identifier from the database."
)
@limiter.limit('5/second')
async def get_me_id(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetch the database ID of the currently authenticated user.
    """
    return await mongodb.get_me_id(current_user.username)

@api_router.get(
    "/welcome/{username}",
    summary="Welcome Message",
    description="Generates a personalized welcome message for the authenticated user.",
    response_description="Returns a welcome message containing the user's username."
)
@limiter.limit('5/second')
async def welcome(
    request: Request,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Generate a personalized welcome message for the authenticated user.
    """
    return {"message": f"Welcome {current_user.username}!"}

@api_router.delete(
    "/users/me",
    summary="Delete Current User",
    description="Permanently deletes the currently authenticated user's account.",
    response_description="Returns a success message after deleting the user account."
)
@limiter.limit('5/second')
async def delete_user(
    request: Request,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Delete the currently authenticated user's account from the system.
    """
    await mongodb.delete_user(current_user.username)
    return {"message": "User deleted successfully"}

@api_router.put(
    "/users/me/email",
    response_model=User,
    summary="Update User Email",
    description="Updates the email address for the currently authenticated user.",
    response_description="Returns the updated user profile with the new email address."
)
@limiter.limit('5/second')
async def update_user_email(
    request: Request,
    email: str,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Update the email address of the currently authenticated user.
    """
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

@api_router.put(
    "/users/me/password",
    response_model=User,
    summary="Update User Password",
    description="Updates the password for the currently authenticated user.",
    response_description="Returns the user profile after successfully updating the password."
)
@limiter.limit('5/second')
async def update_user_password(
    request: Request,
    password: str,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Update the password of the currently authenticated user.
    """
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