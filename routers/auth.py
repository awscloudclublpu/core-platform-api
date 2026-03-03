import os
import secrets
from datetime import datetime, timedelta
from uuid import uuid4

import bcrypt
import pytz
from dotenv import load_dotenv
from fastapi import APIRouter, Cookie, Header, HTTPException, Response, status, Request

from core.auth.jwt import create_access_token
from db.collections import refresh_tokens_collection, users_collection
from models.auth.responses import TokenResponse
from models.auth.utils import hash_refresh_token, rotate_refresh_token, validate_refresh_session
from models.auth.requests import LoginRequest, UserRegisterRequest, GoogleLoginRequest
from models.user import UserDB, UserResponse, AuthProvider
from models.auth.enums import UserRole
from core.logging.audit import audit_log
from core.logging.logger import Logger
from core.security.device import is_new_device
from firebase_admin import auth as firebase_auth

load_dotenv()

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

REFRESH_TOKEN_TLL_DAYS = int(os.getenv("REFRESH_TOKEN_TLL_DAYS", 30))

ASIA_KOLKATA = pytz.timezone("Asia/Kolkata")

# -------------------------------------------------------------------
# REGISTER
# -------------------------------------------------------------------
@auth_router.post("/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@audit_log(action="USER_REGISTER")
async def register_user(payload: UserRegisterRequest):

    users = users_collection()

    payload.email = payload.email.lower().strip()

    if await users.find_one({"email": payload.email}):
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    if await users.find_one({"university_uid": payload.university_uid}):
        raise HTTPException(
            status_code=400,
            detail="University ID already registered",
        )

    password_hash = bcrypt.hashpw(
        payload.password.encode(),
        bcrypt.gensalt(),
    ).decode()

    now = datetime.now(ASIA_KOLKATA)

    user = UserDB(
        id=str(uuid4()),
        **payload.model_dump(exclude={"password"}),
        password_hash=password_hash,

        role=UserRole.attendee,
        auth_provider=AuthProvider.local,
        provider_id=None,

        email_verified=False,
        schema_version=2,
        created_at=now,
        updated_at=now,
    )

    user_dict = user.model_dump()
    user_dict["_id"] = user_dict.pop("id")

    await users.insert_one(user_dict)

    return UserResponse(**user.model_dump(exclude={"password_hash"}))


# -------------------------------------------------------------------
# LOGIN
# -------------------------------------------------------------------

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
    responses={
        200: {
            "description": "Sets refresh token cookie",
            "headers": {
                "Set-Cookie": {
                    "description": "Refresh token (HttpOnly cookie)",
                    "schema": {"type": "string"}
                }
            }
        }
    },
)
@audit_log(action="USER_LOGIN")
async def login_user(
    request: Request,
    payload: LoginRequest,
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
    
    device_id = payload.device_id or str(uuid4())

    new_device = await is_new_device(
        refresh_tokens=refresh_tokens,
        user_id=user["_id"],
        device_id=device_id,
    )

    if new_device:
        await Logger.new_device(
            request=request,
            user_id=user["_id"],
            device_id=device_id,
        )

    access_token = create_access_token(
        user_id=user["_id"],
        role=UserRole(user["role"]),
    )

    # ---------- REFRESH TOKEN ----------
    refresh_token = secrets.token_urlsafe(64)
    refresh_token_hash = hash_refresh_token(refresh_token)

    await refresh_tokens.insert_one(
        {
            "token_hash": refresh_token_hash,
            "user_id": user["_id"],
            "role": user["role"],
            "device_id": device_id,
            "expires_at": datetime.now(ASIA_KOLKATA)
                + timedelta(days=REFRESH_TOKEN_TLL_DAYS),
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

@auth_router.post(
    "/google-login",
    response_model=TokenResponse,
    description="""
    ### Google Login Flow
    Authenticate user with Google ID token.
    Verifies existing account email if not verified else proceeds with login.
    """,
)
@audit_log(action="GOOGLE_LOGIN")
async def google_login(
    request: Request,
    payload: GoogleLoginRequest,
    response: Response,
):
    users = users_collection()
    refresh_tokens = refresh_tokens_collection()

    try:
        decoded_token = firebase_auth.verify_id_token(
            payload.id_token
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    email = decoded_token.get("email")
    email_verified = decoded_token.get("email_verified", False)
    google_uid = decoded_token.get("uid")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google",
        )

    if not email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Google email not verified",
        )

    user = await users.find_one({"email": email})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not registered",
        )

    if not user.get("email_verified"):
        await users.update_one(
            {"_id": user["_id"]},
            {"$set": {"email_verified": True}}
        )

    device_id = payload.device_id or str(uuid4())

    new_device = await is_new_device(
        refresh_tokens=refresh_tokens,
        user_id=user["_id"],
        device_id=device_id,
    )

    if new_device:
        await Logger.new_device(
            request=request,
            user_id=user["_id"],
            device_id=device_id,
        )

    access_token = create_access_token(
        user_id=user["_id"],
        role=UserRole(user["role"]),
    )

    refresh_token = secrets.token_urlsafe(64)
    refresh_token_hash = hash_refresh_token(refresh_token)

    await refresh_tokens.insert_one(
        {
            "token_hash": refresh_token_hash,
            "user_id": user["_id"],
            "role": user["role"],
            "device_id": device_id,
            "expires_at": datetime.now(ASIA_KOLKATA) + timedelta(days=REFRESH_TOKEN_TLL_DAYS),
            "revoked": False,
            "created_at": datetime.now(ASIA_KOLKATA),
            "provider": "google",
            "provider_uid": google_uid,
        }
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=REFRESH_TOKEN_TLL_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=5 * 60,
        email_verified=True,
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
    device_id: str | None = Header(default=None, alias="X-DEVICE-ID"),
):
    if not refresh_token:
        raise HTTPException(401, "Refresh token missing")

    stored_token, token_hash = await validate_refresh_session(
        refresh_token,
        device_id,
    )

    new_refresh_token = await rotate_refresh_token(
        token_hash,
        stored_token,
    )

    access_token = create_access_token(
        user_id=stored_token["user_id"],
        role=UserRole(stored_token["role"]),
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
        email_verified=True,  # optional cached field
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
