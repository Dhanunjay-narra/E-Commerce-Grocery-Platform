"""FastAPI authentication and RBAC permission dependencies."""
from typing import Callable, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token, UserRole, has_permission
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.modules.users.models import User
from app.modules.authentication.repository import AuthRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validates the JWT bearer token and resolves the authenticated User."""
    if not token:
        raise AuthenticationError("Authentication token is missing.")

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if not user_id or token_type != "access":
            raise AuthenticationError("Invalid token format or token type.")
    except Exception as e:
        raise AuthenticationError(f"Could not validate credentials: {str(e)}")

    repo = AuthRepository(db)
    user = await repo.get_user_by_id(user_id)
    if not user:
        raise AuthenticationError("User associated with this token no longer exists.")

    if not user.is_active:
        raise PermissionDeniedError("Your user account has been disabled.")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensures current user is active."""
    return current_user


def require_role(*roles: str) -> Callable:
    """Dependency factory restricting route access to specified roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if UserRole.SUPER_ADMIN.value == current_user.role:
            return current_user
        if current_user.role not in roles:
            raise PermissionDeniedError(
                f"Role '{current_user.role}' is not authorized to access this resource. Allowed: {list(roles)}"
            )
        return current_user

    return role_checker


def require_permission(permission: str) -> Callable:
    """Dependency factory checking fine-grained role permissions."""
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = UserRole(current_user.role)
        if not has_permission(user_role, permission):
            raise PermissionDeniedError(f"Missing required permission: '{permission}'.")
        return current_user

    return permission_checker
