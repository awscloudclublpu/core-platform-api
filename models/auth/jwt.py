from pydantic import BaseModel
from models.auth.enums import UserRole

class JWTPayload(BaseModel):
    sub: str
    role: UserRole
    iss: str
    aud: str
    iat: int
    exp: int
    jti: str
