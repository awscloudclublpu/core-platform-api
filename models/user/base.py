from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from .enums import UserRole

class UserBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone_number: str = Field(min_length=10, max_length=15)

    university_name: str
    university_uid: str

    graduation_year: int = Field(ge=2000, le=2100)
    degree_program: str
    gender: str

    role: UserRole = UserRole.attendee

    hostel: Optional[str] = None
    profile_picture_url: Optional[str] = None
