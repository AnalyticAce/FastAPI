from authentication import (
    get_current_active_user, 
    authenticate_user,
    create_access_token,
)
from authentication import app, db, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from models import Token, User, LogoutResponse

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    
    # hashed_password = form_data.password
    # if not hashed_password == user.hashed_password:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        'access_token': access_token,
        "token_type": "Bearer"
    }

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/logout", response_model=LogoutResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    revoked_tokens.add(current_user.token)
    return {"message": "Successfully logged out"}

@app.get("/users/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": 1, "owner": current_user}]

@app.get("/welcome/{username}")
async def welcome(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Welcome {current_user.username}!"}