from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from uuid import uuid4

from db.collections import registration_collection, users_collection
from core.auth.dependencies import require_role
from models.auth.enums import UserRole
from models.auth.jwt import JWTPayload

attendance_router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)