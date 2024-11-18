from fastapi import APIRouter, Depends, HTTPException, Request, status, Security
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm, APIKeyHeader
from datetime import timedelta
import httpx
from utils.auth_utils import (
    mongodb,
    authenticate_user,
    create_access_token,
    get_password_hash
)
from routers.models import Token, User, UserCreate
from routers.limiter import limiter
from utils.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    ACTIVATE_OAUTH2,
    ACTIVATE_GITHUB,
    ACTIVATE_MICROSOFT
)

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication / Identification"],
    responses={
        404: {"description": "Endpoint not found"},
        403: {"description": "Forbidden access"},
        200: {"description": "Success response"},
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized access"}
    }
)

API_KEYS = [
    "b63079cf984468d7ab1efaf1e5557a719b9f5eb05d88fd6abfa5d469e0a64e23",
    "e08a686055f250932cba6aa53126ec9fd7d1d51f38012e37785573893dadadcc",
    "197138fd0ab4af061a1a3d1044df7f10f2d93c7a1596c12695f1b73cc1afab68",
]

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header in API_KEYS:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid or missing header key provided"
    )

@auth_router.post(
    "/token",
    response_model=Token,
    summary="Login User",
    description="Authenticates a user and provides a JWT access token for subsequent requests.",
    response_description="Returns an access token and token type for authenticated user."
)
@limiter.limit('1/second')
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    Authenticate user and generate access token.
    """
    user = await authenticate_user(form_data.username, form_data.password)
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

@auth_router.post(
    "/register",
    response_model=User,
    summary="Register New User",
    description="Creates a new user account with the provided username, email, and password.",
    response_description="Returns the created user's profile information (excluding password)."
)
@limiter.limit('1/second')
async def register_user(
    request: Request,
    user: UserCreate,
) -> User:
    """
    Register a new user in the system.
    """
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
        "disabled": False,
        "is_superuser": False
    }
    
    result = await mongodb.create_user(user_data)
    return User(username=user.username, email=user.email, disabled=False)

if ACTIVATE_OAUTH2 and ACTIVATE_GITHUB:
    @auth_router.get(
        '/github-login',
        summary="GitHub OAuth Login",
        description="Initiates the GitHub OAuth2 authentication flow by redirecting to GitHub's authorization page.",
        response_description="Redirects user to GitHub's authorization page."
    )
    @limiter.limit('1/second')
    async def github_login(request: Request) -> RedirectResponse:
        """
        Initiate GitHub OAuth login flow.
        """
        return RedirectResponse(
            f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}', 
            status_code=302
        )

    @auth_router.get(
        '/github-code',
        summary="GitHub OAuth Callback",
        description="Handles the GitHub OAuth2 callback, exchanges the code for an access token, and creates/updates user account.",
        response_description="Returns a JWT access token for the authenticated GitHub user."
    )
    @limiter.limit('1/second')
    async def github_code(
        request: Request,
        code: str
    ) -> dict:
        """
        Handle GitHub OAuth callback and authenticate user.
        """
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

        email = github_user_data.get("email")
        username = github_user_data.get("login")

        existing_user = await mongodb.get_user_by_username(username)
        if not existing_user:
            new_user_data = {
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
    
if ACTIVATE_OAUTH2 and ACTIVATE_MICROSOFT:
    @auth_router.get(
        '/microsoft-login',
        summary="Microsoft OAuth Login",
        description="Initiates the Microsoft OAuth2 authentication flow by redirecting to Microsoft's authorization page.",
        response_description="Redirects user to Microsoft's authorization page."
    )
    @limiter.limit('1/second')
    def microsoft_login(request: Request) -> RedirectResponse:
        pass