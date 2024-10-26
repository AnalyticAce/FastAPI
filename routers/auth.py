from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import httpx
from utils.auth_utils import AuthUtils
from routers.models import Token, User, UserCreate
from db.mongo import Mongo
from utils.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    ACTIVATE_OAUTH2,
    ACTIVATE_GITHUB, 
    MONGO_DB_NAME, 
    MONGO_COLLECTION_NAME_USER
)

mongodb = Mongo(MONGO_DB_NAME, MONGO_COLLECTION_NAME_USER)

async def main():
    await mongodb.create_db(MONGO_DB_NAME)
    await mongodb.create_collection(MONGO_COLLECTION_NAME_USER)

auth_utils = AuthUtils(mongodb)

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@auth_router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_utils.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = auth_utils.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/register", response_model=User)
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
    
    hashed_password = auth_utils.get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "disabled": False
    }
    
    result = await mongodb.create_user(user_data)
    return User(username=user.username, email=user.email, disabled=False)

if ACTIVATE_OAUTH2 and ACTIVATE_GITHUB:
    @auth_router.get('/github-login')
    async def github_login():
        return RedirectResponse(
            f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}', 
            status_code=302
        )

    @auth_router.get('/github-code')
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
        jwt_token = auth_utils.create_access_token(token_data)

        return {"access_token": jwt_token, "token_type": "bearer"}
