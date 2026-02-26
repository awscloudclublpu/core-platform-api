from functools import wraps
from fastapi import Request
from core.logging.logger import Logger


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