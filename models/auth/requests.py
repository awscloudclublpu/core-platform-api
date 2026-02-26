from pydantic import BaseModel, EmailStr, Field
from models.user import UserBase


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    device_id: str = Field(default=None)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class UserRegisterRequest(UserBase):
    email: EmailStr
    password: str = Field(min_length=8)
    device_id: str = Field(default=None)
