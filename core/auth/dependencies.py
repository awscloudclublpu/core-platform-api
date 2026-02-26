from fastapi import Depends, HTTPException, status

from core.auth.jwt import get_current_user
from models.auth.jwt import JWTPayload
from models.auth.enums import UserRole


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory to enforce role-based access control.

    Usage:
        Depends(require_role(UserRole.core))
        Depends(require_role(UserRole.manager, UserRole.core))
    """

    def checker(
            payload: JWTPayload = Depends(get_current_user),
        ) -> JWTPayload:

            if allowed_roles and payload.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

            return payload

    return checker