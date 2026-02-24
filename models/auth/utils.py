
import datetime
import hashlib
import os
from fastapi import HTTPException
import pytz
from db.collections import refresh_tokens_collection
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

REFRESH_TOKEN_TLL_DAYS = int(os.getenv("REFRESH_TOKEN_TLL_DAYS", 30))

ASIA_KOLKATA = pytz.timezone("Asia/Kolkata")

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

async def validate_refresh_session(
    refresh_token: str,
    device_id: str | None,
):
    refresh_tokens = refresh_tokens_collection()

    token_hash = hash_refresh_token(refresh_token)

    stored = await refresh_tokens.find_one(
        {
            "token_hash": token_hash,
            "revoked": False,
            "expires_at": {"$gt": datetime.now(ASIA_KOLKATA)},
        }
    )

    if not stored:
        raise HTTPException(401, "Invalid or expired refresh token")

    stored_device = stored.get("device_id")

    if stored_device and device_id and stored_device != device_id:
        await refresh_tokens.update_one(
            {"token_hash": token_hash},
            {"$set": {"revoked": True}},
        )
        raise HTTPException(401, "Device mismatch")
    
    await refresh_tokens.update_one(
        {"token_hash": token_hash},
        {
            "$set": {
                "last_used_at": datetime.now(ASIA_KOLKATA)
            }
        }
    )
    
    return stored, token_hash

async def rotate_refresh_token(old_hash, stored_token):
    refresh_tokens = refresh_tokens_collection()

    await refresh_tokens.update_one(
        {"token_hash": old_hash},
        {"$set": {"revoked": True}}
    )

    new_token = secrets.token_urlsafe(64)
    new_hash = hash_refresh_token(new_token)

    await refresh_tokens.insert_one({
        "token_hash": new_hash,
        "user_id": stored_token["user_id"],
        "role": stored_token["role"],
        "device_id": stored_token["device_id"],
        "expires_at": datetime.now(ASIA_KOLKATA)
            + timedelta(days=REFRESH_TOKEN_TLL_DAYS),
        "revoked": False,
        "created_at": datetime.now(ASIA_KOLKATA),
    })

    return new_token