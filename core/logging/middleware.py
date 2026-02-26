from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

from core.logging.logger import Logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    LOGGED_TAGS = {"Authentication"}

    async def dispatch(self, request: Request, call_next):

        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            latency = (time.perf_counter() - start) * 1000
            await Logger.api(request, 500, latency)
            raise

        latency = (time.perf_counter() - start) * 1000

        route = request.scope.get("route")
        if route:
            tags = getattr(route, "tags", [])
            if any(tag in self.LOGGED_TAGS for tag in tags):
                await Logger.api(request, response.status_code, latency)

        return response