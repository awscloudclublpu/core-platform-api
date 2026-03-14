import os
import hmac
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

CLIENT_API_KEY = os.getenv("CLIENT_API_KEY")


class ApiKeyMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        if request.url.path.startswith(("/docs", "/openapi", "/docs/v2")):
            return await call_next(request)

        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "detail": "Missing API Key"
                }
            )

        if not hmac.compare_digest(api_key, CLIENT_API_KEY):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "success": False,
                    "detail": "Invalid API Key"
                }
            )

        device_id = request.headers.get("X-DEVICE-ID")
        if not device_id:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "detail": "Missing Device ID"
                }
            )

        return await call_next(request)