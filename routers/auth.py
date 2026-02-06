from fastapi import APIRouter, HTTPException, status, Response, Cookie
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
    tags=["Authentication"],
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
@auth_router.post("/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    description="""
    ### Register Flow
    Register a new user with email and password.
    Returns the created user details (excluding password).
    Validations:
    - Email must be unique.
    - Password is hashed before storage.
    """,
)
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

@auth_router.post(
    "/login",
    response_model=TokenResponse,
    description="""
    ### Login Flow
    Authenticate user with email and password.
    Returns an access token (JWT) and sets a refresh token as an HTTP-only cookie.
    Validations:
    - Validates email and password.
    """,
)
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

# -------------------------------------------------------------------
# REFRESH TOKEN
# -------------------------------------------------------------------

@auth_router.post(
    "/refresh",
    response_model=TokenResponse,
    description="""
    ### Refresh Token Flow
    Issues a new access token using a valid refresh token.
    - Refresh token must be present in HTTP-only cookie.
    - Refresh token is rotated on every use.
    """,
)
async def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    refresh_tokens = refresh_tokens_collection()
    users = users_collection()

    refresh_token_hash = hash_refresh_token(refresh_token)

    stored_token = await refresh_tokens.find_one(
        {
            "token_hash": refresh_token_hash,
            "revoked": False,
            "expires_at": {"$gt": datetime.now(ASIA_KOLKATA)},
        }
    )

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = await users.find_one({"id": stored_token["user_id"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # ---------- ROTATE REFRESH TOKEN ----------
    await refresh_tokens.update_one(
        {"token_hash": refresh_token_hash},
        {"$set": {"revoked": True}}
    )

    new_refresh_token = secrets.token_urlsafe(64)
    new_refresh_token_hash = hash_refresh_token(new_refresh_token)

    await refresh_tokens.insert_one(
        {
            "token_hash": new_refresh_token_hash,
            "user_id": user["id"],
            "expires_at": datetime.now(ASIA_KOLKATA)
            + timedelta(days=REFRESH_TOKEN_TLL_DAYS),
            "revoked": False,
            "created_at": datetime.now(ASIA_KOLKATA),
        }
    )

    # ---------- NEW ACCESS TOKEN ----------
    access_token = create_access_token(
        user_id=user["id"],
        role=UserRole(user["role"]),
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=REFRESH_TOKEN_TLL_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=5 * 60,
        email_verified=user.get("email_verified", False),
    )

# -------------------------------------------------------------------
# LOGOUT
# -------------------------------------------------------------------

@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    description="""
    ### Logout Flow
    Revokes the refresh token and clears authentication cookies.
    """,
)
async def logout_user(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
):
    if refresh_token:
        refresh_tokens = refresh_tokens_collection()
        refresh_token_hash = hash_refresh_token(refresh_token)

        await refresh_tokens.update_one(
            {"token_hash": refresh_token_hash},
            {"$set": {"revoked": True}}
        )

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return None
