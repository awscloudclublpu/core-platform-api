
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from uuid import uuid4
from bson import ObjectId

from db.collections import registration_collection
from core.auth.dependencies import require_role
from models.user.enums import UserRole
from models.auth.jwt import JWTPayload

from models.registrations import (
    EventRegistrationRequest,
    EventRegistrationCheck,
    EventRegistrationCancellation,
    RegistrationResponse,
    RegistrationStatusResponse,
    RegistrationCancellationResponse,
)

registrations_router = APIRouter(
    prefix="/registrations",
    tags=["Registrations"],
)

def get_registrations():
    return registration_collection()

def require_logged_in():
    return Depends(require_role())

@registrations_router.post(
    "",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_for_event(
    payload: EventRegistrationRequest,
    current_user: JWTPayload = Depends(require_role()),
):
    registrations = get_registrations()
    now = datetime.now(timezone.utc)

    event_id = ObjectId(payload.event_id)

    existing = await registrations.find_one({
        "event_id": event_id,
        "university_uid": payload.university_uid,
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already registered for this event.")

    reg_doc = {
        "event_id": event_id,
        "university_uid": payload.university_uid,
        "registered_at": now,
    }
    await registrations.insert_one(reg_doc)
    return RegistrationResponse(
        event_id=reg_doc["event_id"],
        university_uid=reg_doc["university_uid"],
        registered_at=reg_doc["registered_at"],
    )

@registrations_router.get(
    "/status",
    response_model=RegistrationStatusResponse,
)
async def check_registration_status(
    payload: EventRegistrationCheck = Depends(),
    current_user: JWTPayload = Depends(require_role()),
):
    registrations = get_registrations()
    event_id = ObjectId(payload.event_id)
    reg = await registrations.find_one({
        "event_id": event_id,
        "university_uid": current_user.university_uid,
    })
    return RegistrationStatusResponse(
        event_id=event_id,
        is_registered=bool(reg),
    )

@registrations_router.delete(
    "",
    response_model=RegistrationCancellationResponse,
)
async def cancel_registration(
    payload: EventRegistrationCancellation,
    current_user: JWTPayload = Depends(require_role()),
):
    registrations = get_registrations()
    event_id = ObjectId(payload.event_id)
    result = await registrations.delete_one({
        "event_id": event_id,
        "university_uid": current_user.university_uid,
    })
    cancelled = result.deleted_count > 0
    return RegistrationCancellationResponse(
        event_id=event_id,
        cancelled=cancelled
    )