async def is_new_device(refresh_tokens, user_id: str, device_id: str) -> bool:
    """
    Returns True if user logs in from unseen device.
    """

    existing = await refresh_tokens.find_one({
        "user_id": user_id,
        "device_id": device_id,
        "revoked": False,
    })

    return existing is None