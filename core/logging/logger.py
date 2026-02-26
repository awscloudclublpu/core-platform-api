from functools import wraps
from fastapi import Request

from core.logging.transport import (
    enqueue_api_log,
    enqueue_audit_log,
    build_api_embed,
    build_audit_embed,
    build_new_device_embed,
)


class Logger:

    # ---------------- API LOG ----------------
    @staticmethod
    async def api(request: Request, status: int, latency_ms: float | None = None):
        trace_id = getattr(request.state, "trace_id", "unknown")
        embed = build_api_embed(
            request.method,
            request.url.path,
            status,
            request.headers.get("X-DEVICE-ID"),
            request.client.host if request.client else "unknown",
            getattr(request.state, "user_id", None),
            latency_ms,
            trace_id,
        )
        await enqueue_api_log(embed)

    # ---------------- AUDIT LOG ----------------
    @staticmethod
    async def audit(request: Request, action: str):
        trace_id = getattr(request.state, "trace_id", "unknown")
        embed = build_audit_embed(
            action,
            request.method,
            request.url.path,
            request.headers.get("X-DEVICE-ID"),
            request.client.host if request.client else "unknown",
            getattr(request.state, "user_id", None),
            trace_id,
        )
        await enqueue_audit_log(embed)

    # ---------------- NEW DEVICE ----------------
    @staticmethod
    async def new_device(request: Request, user_id: str, device_id: str):
        trace_id = getattr(request.state, "trace_id", "unknown")
        embed = build_new_device_embed(
            user_id,
            device_id,
            request.client.host if request.client else "unknown",
            trace_id,
        )
        await enqueue_audit_log(embed)

    # ---------------- DECORATOR ----------------
    @staticmethod
    def audit_log(action: str):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):

                request = kwargs.get("request")

                if not request:
                    for arg in args:
                        if isinstance(arg, Request):
                            request = arg
                            break

                response = await func(*args, **kwargs)

                if request:
                    await Logger.audit(request, action)

                return response

            return wrapper
        return decorator