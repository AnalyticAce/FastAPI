from fastapi import APIRouter, Request
from routers.limiter import limiter

app_health = APIRouter(
    prefix="/health",
    tags=["Health Check"]
)

@app_health.get("/")
@limiter.limit('1/second')
async def health_check(request: Request):
    return {"message": "Server is running :) !"}