from fastapi import APIRouter, Request
from routers.limiter import limiter
from datetime import datetime

app_health = APIRouter(
    prefix="/health",
    tags=["Health Check"]
)

app_about = APIRouter(
    tags=["About"]
)

@app_health.get("/")
@limiter.limit('1/second')
async def health_check(request: Request):
    return {"message": "Server is running :) !"}


# The following properties are required:
# • client.host indicates the IP address of the client performing the HTTP request
# • server.current_time indicates the server time in the Epoch Unix Time Stamp format
# • server.services indicates the list of services supported by the server
# • server.services[].name indicates the name of the service
# • server.services[].actions indicates the list of Actions supported by this service
# • server.services[].actions[]. name indicates the identifier of this Action
# • server.services[].actions[]. description indicates the description of this Action
# • server.services[].reactions indicates the list of REActions supported by this service
# • server.services[].actions[]. name indicates the identifier of this REAction
# • server.services[].actions[]. description indicates the description of this REAction

about_dict = {
    "client": {
        "host": "127.0.0.1"
    },
    "server": {
        "current_time": datetime.now().timestamp(),
        "services": [
            {
                "name": "Service 1",
                "actions": [
                    {
                        "name": "Service 1",
                        "description": "Service 1"
                    }
                ],
                "reactions": [
                    {
                        "name": "Service 1",
                        "description": "Service 1"
                    }
                ]
            },
            {
                "name": "About",
                "actions": [],
                "reactions": []
            }
        ]
    }
}
@app_about.get("/about.json")
@limiter.limit('1/second')
async def about(request: Request):
    return about_dict