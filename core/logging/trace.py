import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TraceIDMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        request.state.trace_id = uuid.uuid4().hex[:8]
        response = await call_next(request)

        # optional: expose to frontend/debugging
        response.headers["X-Trace-ID"] = request.state.trace_id
        return response