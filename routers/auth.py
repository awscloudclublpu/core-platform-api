from fastapi import APIRouter, HTTPException, status, Response
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import bcrypt
import secrets
import hashlib
import pytz

from models.user import UserRegisterRequest, UserResponse, UserDB
from models.auth.responses import TokenResponse
from models.user.enums import UserRole

from db.collections import users_collection, refresh_tokens_collection
from core.auth.jwt import create_access_token

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

REFRESH_TOKEN_TLL_DAYS = 30

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

ASIA_KOLKATA = pytz.timezone("Asia/Kolkata")

# -------------------------------------------------------------------
# REGISTER
# -------------------------------------------------------------------
@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegisterRequest):
    users = users_collection()

    existing = await users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    password_hash = bcrypt.hashpw(
        payload.password.encode(),
        bcrypt.gensalt(),
    ).decode()

    now = datetime.now(ASIA_KOLKATA)

    user = UserDB(
        **payload.model_dump(exclude={"password"}),
        role=UserRole.attendee,
        password_hash=password_hash,
        is_verified=False,
        created_at=now,
        updated_at=now,
    )

    await users.insert_one(user.model_dump())

    return UserResponse(
        **user.model_dump(
            exclude={"password_hash"}
        )
    )

# -------------------------------------------------------------------
# LOGIN
# -------------------------------------------------------------------
from models.user.requests import UserLoginRequest

@auth_router.post("/login", response_model=TokenResponse)
async def login_user(
    payload: UserLoginRequest,
    response: Response,
):
    users = users_collection()
    refresh_tokens = refresh_tokens_collection()

    user = await users.find_one(
        {
            "email": payload.email
        }
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
        )

    if not bcrypt.checkpw(
        payload.password.encode(),
        user['password_hash'].encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # ---------- JWT ----------
    access_token = create_access_token(
        user_id=user["id"],
        role=UserRole(user["role"]),
    )

    # ---------- REFRESH TOKEN ----------
    refresh_token = secrets.token_urlsafe(64)
    refresh_token_hash = hash_refresh_token(refresh_token)

    await refresh_tokens.insert_one(
        {
            "token_hash": refresh_token_hash,
            "user_id": user["id"],
            "expires_at": datetime.now(ASIA_KOLKATA) + timedelta(days=REFRESH_TOKEN_TLL_DAYS),
            "revoked": False,
            "created_at": datetime.now(ASIA_KOLKATA),
        }
    )

    #HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=REFRESH_TOKEN_TLL_DAYS * 24 * 60 * 60
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=5 * 60,
        email_verified=user.get("email_verified", False),
    )