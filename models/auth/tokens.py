from datetime import datetime
from pydantic import BaseModel

class RefreshTokenDB(BaseModel):
    token_hash: str
    user_id: str
    expires_at: datetime
    revoked: bool = False
    created_at: datetime
    last_used_at: datetime | None = None
    device_id: str | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
