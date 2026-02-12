
from pydantic import BaseModel, Field, EmailStr

class EventRegistrationRequest(BaseModel):
    event_id: str = Field(..., description="The ID of the event")
    university_uid: str = Field(..., description="The university UID of the registrant")


class EventRegistrationCheck(BaseModel):
    event_id: str = Field(..., description="The ID of the event")


class EventRegistrationCancellation(BaseModel):
    event_id: str = Field(..., description="The ID of the event")