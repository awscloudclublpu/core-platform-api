from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from models.auth.enums import UserRole


class AuthProvider(str, Enum):
    local = "local"
    google = "google"


class UserBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr

    phone_number: str = Field(
        min_length=10,
        max_length=10,
        pattern=r"^[0-9]{10}$"
    )

    university_name: str
    university_uid: str
    graduation_year: int = Field(ge=2000, le=2100)
    degree_program: str

    gender: Optional[str] = None
    hostel: Optional[str] = None
    profile_picture_url: Optional[str] = None