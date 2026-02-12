from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class RegistrationResponse(BaseModel):
    event_id: str = Field(..., description="The ID of the event")
    university_uid: str = Field(..., description="The university UID of the registrant")
    registered_at: datetime = Field(..., description="The registration timestamp")


class RegistrationStatusResponse(BaseModel):
    event_id: str = Field(..., description="The ID of the event")
    is_registered: bool = Field(..., description="Whether the user is registered for the event")


class RegistrationCancellationResponse(BaseModel):
    event_id: str = Field(..., description="The ID of the event")
    cancelled: bool = Field(..., description="Whether the registration was cancelled successfully")
