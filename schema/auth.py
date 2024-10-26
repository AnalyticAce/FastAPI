from pydantic import BaseModel

class OAuthResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str

class GitHubUser(BaseModel):
    id: int
    login: str
    email: str | None = None