
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timedelta, timezone
from uuid import uuid4
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from models.auth.jwt import JWTPayload
from models.user.enums import UserRole

# -------------------------------------------------------------------
# Config (read once)
# -------------------------------------------------------------------

JWT_ISSUER = os.getenv("JWT_ISSUER", "horizon.auth")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "horizon.api")
JWT_ALGORITHM = "RS256"
ACCESS_TOKEN_TTL_MINUTES = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "5"))

# RSA keys (recommended)
JWT_PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY")
JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")

if not JWT_PRIVATE_KEY or not JWT_PUBLIC_KEY:
    raise RuntimeError("JWT_PRIVATE_KEY or JWT_PUBLIC_KEY not set")

# -------------------------------------------------------------------
# Security scheme
# -------------------------------------------------------------------

security = HTTPBearer(auto_error=False)

# -------------------------------------------------------------------
# Token creation
# -------------------------------------------------------------------

def create_access_token(
    *,
    user_id: str,
    role: UserRole,
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "role": role.value,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES)).timestamp()),
        "jti": str(uuid4()),
    }

    token = jwt.encode(
        payload,
        JWT_PRIVATE_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return token

# -------------------------------------------------------------------
# Token verification
# -------------------------------------------------------------------

def verify_access_token(token: str) -> JWTPayload:
    try:
        decoded = jwt.decode(
            token,
            JWT_PUBLIC_KEY,
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
        )
        return JWTPayload.model_validate(decoded)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

# -------------------------------------------------------------------
# FastAPI dependency
# -------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> JWTPayload:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    return verify_access_token(credentials.credentials)
