from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from uuid import uuid4

from db.collections import event_collection
from core.auth.dependencies import require_role
from models.auth.enums import UserRole
from models.auth.jwt import JWTPayload

from models.event import (
    EventCreateRequest,
    EventUpdateRequest,
    EventResponse,
    EventDetails,
    EventDB,
    EventStatus,
)

event_router = APIRouter(
    prefix="/events",
    tags=["Events"],
)

@event_router.post(
    "",
    response_model=EventDetails,
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
    payload: EventCreateRequest,
    current_user: JWTPayload = Depends(require_role(UserRole.core)),
):
    events = event_collection()
    now = datetime.now(timezone.utc)

    event = EventDB(
        id=str(uuid4()),
        **payload.model_dump(),
        status=EventStatus.draft,
        created_by=current_user.sub,
        registered_count=0,
        created_at=now,
        updated_at=now,
    )

    await events.insert_one(event.model_dump())

    return EventDetails(
        **event.model_dump()
    )

@event_router.put(
    "/{id}",
    response_model=EventDetails,
)
async def update_event(
    event_id: str,
    payload: EventUpdateRequest,
    current_user: JWTPayload = Depends(require_role(UserRole.core)),
):
    events = event_collection()
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = await events.find_one_and_update(
        {"id": event_id},
        {"$set": update_data},
        return_document=True,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return EventDetails(**result)

@event_router.get(
    "",
    response_model=list[EventResponse],
)
async def list_events():
    events = event_collection()

    cursor = events.find(
        {"status": EventStatus.published}
    ).sort("start_time", 1)

    result = []
    async for event in cursor:
        result.append(EventResponse(**event))

    return result

@event_router.get(
    "/{id}",
    response_model=EventDetails,
)
async def get_event_details(event_id: str):
    events = event_collection()

    event = await events.find_one(
        {"id": event_id, "status": EventStatus.published}
    )

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return EventDetails(**event)
