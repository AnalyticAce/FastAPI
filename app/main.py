from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth.auth import auth_router
from routers.api.api import api_router
from routers.other.health import app_health, app_about
import uvicorn

app = FastAPI(
    title="FastAPI JWT Template",
    summary="This is a template for FastAPI with authentication logic using JWT",
    version="1.0.0",
)

origins = [
    "127.0.0.1:8000/docs"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(api_router)
app.include_router(app_health)
app.include_router(app_about)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True
    )