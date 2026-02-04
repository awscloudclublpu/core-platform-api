from pydantic import BaseModel, Field
from .base import UserBase

class UserRegisterRequest(UserBase):
    password: str = Field(min_length=8)

class UserLoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)