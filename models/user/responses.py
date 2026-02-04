from datetime import datetime
from pydantic import Field
from .base import UserBase

class UserResponse(UserBase):
    id: str = Field(alias="_id")
    is_verified: bool
    created_at: datetime
