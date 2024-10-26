from fastapi.responses import RedirectResponse
from authentication import (
    get_current_active_user, 
    authenticate_user,
    get_password_hash,
    create_access_token,
)
from authentication import app, mongodb
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from models import Token, User, UserCreate
from config import (
    ACCESS_TOKEN_EXPIRE_MINUTES, GITHUB_CLIENT_ID, 
    GITHUB_CLIENT_SECRET, ACTIVATE_OAUTH2, ACTIVATE_GITHUB,
    ACTIVATE_GOOGLE
)
import httpx

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

@app.get("/users/me/id", tags=["User Management"])
async def get_me_id(current_user: User = Depends(get_current_active_user)):
    return await mongodb.get_me_id(current_user.username)

@app.get("/welcome/{username}", tags=["User Management"])
async def welcome(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Welcome {current_user.username}!"}

@app.delete("/users/me", tags=["User Management"])
async def delete_user(current_user: User = Depends(get_current_active_user)):
    await mongodb.delete_user(current_user.username)
    return {"message": "User deleted successfully"}

@app.put("/users/me/{email}", response_model=User, tags=["User Management"])
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

@app.put("/users/me/{password}", response_model=User, tags=["User Management"])
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


if ACTIVATE_OAUTH2:
    
    if ACTIVATE_GITHUB:
        
        @app.get('/github-login', tags=["OAuth2"])
        async def github_login():
            return RedirectResponse(
                f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}', 
                status_code=302
                )

        @app.get('/github-code', tags=["OAuth2"])
        async def github_code(code: str):
            token_params = {
                'client_id': GITHUB_CLIENT_ID,
                'client_secret': GITHUB_CLIENT_SECRET,
                'code': code
            }
            headers = {'Accept': 'application/json'}
            
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    url='https://github.com/login/oauth/access_token',
                    params=token_params,
                    headers=headers
                )
            
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            if not access_token:
                raise HTTPException(status_code=400, detail="Failed to fetch access token from GitHub")

            headers.update({'Authorization': f'Bearer {access_token}'})
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    url='https://api.github.com/user',
                    headers=headers
                )
            github_user_data = user_response.json()

            github_id = github_user_data.get("id")
            email = github_user_data.get("email")
            username = github_user_data.get("login")

            existing_user = await mongodb.get_user_by_github_id(github_id)
            if not existing_user:
                new_user_data = {
                    "github_id": github_id,
                    "username": username,
                    "email": email,
                    "hashed_password": None,
                    "disabled": False
                }
                await mongodb.create_user(new_user_data)
                user = new_user_data
            else:
                user = existing_user

            token_data = {"sub": user["username"]}
            jwt_token = create_access_token(token_data)

            return {"access_token": jwt_token, "token_type": "bearer"}

    GOOGLE_CLIENT_ID = "jj"
    GOOGLE_CLIENT_SECRET = "f"
    GOOGLE_REDIRECT_URI = "http://localhost:8000/google-code"
    FRONTEND_URL = "127.0.0.1/docs"

    if ACTIVATE_GOOGLE:
        
        @app.get('/google-login', tags=["OAuth2"])
        async def google_login():
            pass