from datetime import datetime
from pydantic import BaseModel
from .base import UserBase

class UserDB(UserBase):
    id: str
    password_hash: str
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime
