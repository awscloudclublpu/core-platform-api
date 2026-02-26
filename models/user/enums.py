import warnings
from models.auth.enums import UserRole as _UserRole

warnings.warn(
    "Importing `models.user.enums.UserRole` is deprecated — use `models.auth.enums.UserRole` instead.",
    DeprecationWarning,
    stacklevel=2,
)

UserRole = _UserRole

__all__ = ["UserRole"]
