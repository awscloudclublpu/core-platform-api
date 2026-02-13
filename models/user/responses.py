from datetime import datetime
from pydantic import Field
from .base import UserBase

class UserResponse(UserBase):
    id: str
    is_verified: bool
    created_at: datetime
