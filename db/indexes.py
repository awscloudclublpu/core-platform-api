from pymongo import ASCENDING
from .collections import users_collection, refresh_tokens_collection


async def create_indexes() -> None:
    await users_collection().create_index(
        [("email", ASCENDING)], unique=True
    )

    await users_collection().create_index(
        [("university_uid", ASCENDING)], unique=True
    )

    await refresh_tokens_collection().create_index(
        [("token_hash", ASCENDING)], unique=True
    )

    # TTL index → auto-delete expired refresh tokens
    await refresh_tokens_collection().create_index(
        [("expires_at", ASCENDING)],
        expireAfterSeconds=0
    )
