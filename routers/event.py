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
    description="Create a new event"
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
        registered_count=0 if payload.registration_mode == "internal" else None,
        created_at=now,
        updated_at=now,
    )

    await events.insert_one(event.model_dump())
    return EventDetails(**event.model_dump())

@event_router.put(
    "/{event_id}",
    response_model=EventDetails,
    description="Update an existing event"
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

@event_router.patch(
    "/{event_id}/publish",
    response_model=EventDetails,
)
async def publish_event(
    event_id: str,
    current_user: JWTPayload = Depends(require_role(UserRole.core)),
):
    events = event_collection()

    event = await events.find_one({"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event["status"] == EventStatus.published:
        raise HTTPException(status_code=400, detail="Event already published")

    required_fields = [
        "title",
        "start_time",
        "end_time",
        "short_description",
        "description",
        "banner_url",
        "registration_mode",
    ]

    for field in required_fields:
        if not event.get(field):
            raise HTTPException(
                status_code=400,
                detail=f"{field} is required before publishing",
            )

    if event["registration_mode"] == "external":
        if not event.get("meetup_url"):
            raise HTTPException(
                status_code=400,
                detail="meetup_url is required for external events",
            )

    if event["registration_mode"] == "internal":
        if event.get("price") and not event.get("currency"):
            raise HTTPException(
                status_code=400,
                detail="currency is required for paid events",
            )

    result = await events.find_one_and_update(
        {"id": event_id},
        {
            "$set": {
                "status": EventStatus.published,
                "updated_at": datetime.now(timezone.utc),
            }
        },
        return_document=True,
    )

    return EventDetails(**result)

@event_router.patch(
    "/{event_id}/cancel",
    response_model=EventDetails,
)
async def cancel_event(
    event_id: str,
    current_user: JWTPayload = Depends(require_role(UserRole.core)),
):
    events = event_collection()

    result = await events.find_one_and_update(
        {"id": event_id},
        {"$set": {
            "status": EventStatus.cancelled,
            "updated_at": datetime.now(timezone.utc),
        }},
        return_document=True,
    )

    if not result:
        raise HTTPException(status_code=404, detail="Event not found")

    return EventDetails(**result)

@event_router.get(
    "/admin/all",
    response_model=list[EventDetails],
    description="List all events (admin only)"
)
async def list_all_events(
    current_user: JWTPayload = Depends(require_role(UserRole.core)),
):
    events = event_collection()

    cursor = events.find().sort("created_at", -1)

    result = []
    async for event in cursor:
        result.append(EventDetails(**event))

    return result

@event_router.get(
    "",
    response_model=list[EventResponse],
    description="List all published events"
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
    "/{event_id}",
    response_model=EventDetails,
    description="Get event details"
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