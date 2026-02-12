from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from datetime import datetime
from .enums import ActionType

class AttendanceRequest(BaseModel):
    email: EmailStr = Field(..., description="The email address of the attendee")
    eventId: ObjectId = Field(..., description="The ID of the event")
    actionType: ActionType = Field(..., description="The type of action (checkin or checkout)")