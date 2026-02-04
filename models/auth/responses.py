from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds
    email_verified: bool


class TokenResponseWithRefresh(TokenResponse):
    refresh_token: str


class AuthErrorResponse(BaseModel):
    error: str
    error_description: str
