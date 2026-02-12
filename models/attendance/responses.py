from pydantic import BaseModel, EmailStr, StrictBool, Field
from bson import ObjectId
from .enums import ActionType

class AttendanceResponse(BaseModel):
    email: EmailStr = Field(..., description="The email address of the attendee")
    eventId: ObjectId = Field(..., description="The ID of the event")
    actionType: ActionType = Field(..., description="The type of action (checkin or checkout)")
    success: StrictBool = Field(..., description="Indicates if the attendance action was successful")