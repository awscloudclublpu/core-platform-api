from datetime import datetime
from typing import Optional

from models.auth.enums import UserRole
from .base import AuthProvider, UserBase

class UserDB(UserBase):
    id: str
    password_hash: str

    role: UserRole = UserRole.attendee
    auth_provider: AuthProvider = AuthProvider.local
    provider_id: Optional[str] = None

    email_verified: bool = False
    schema_version: int = 2

    created_at: datetime
    updated_at: datetime