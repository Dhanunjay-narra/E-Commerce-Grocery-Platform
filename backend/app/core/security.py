"""Security utilities: password hashing, JWT token handling, OTPs, and RBAC roles."""
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(str, Enum):
    """Platform Role-Based Access Control roles."""
    CUSTOMER = "CUSTOMER"
    VENDOR_OWNER = "VENDOR_OWNER"
    VENDOR_STAFF = "VENDOR_STAFF"
    DELIVERY_AGENT = "DELIVERY_AGENT"
    SUPPORT_AGENT = "SUPPORT_AGENT"
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


ROLE_PERMISSIONS: Dict[UserRole, Set[str]] = {
    UserRole.CUSTOMER: {
        "profile:read", "profile:write",
        "cart:read", "cart:write",
        "orders:create", "orders:read_own", "orders:cancel_own",
        "reviews:create", "wishlist:manage",
        "household:manage",
    },
    UserRole.VENDOR_STAFF: {
        "store:read",
        "products:read",
        "inventory:read", "inventory:update",
        "orders:fulfill", "orders:read_vendor",
    },
    UserRole.VENDOR_OWNER: {
        "store:read", "store:write",
        "products:read", "products:write",
        "inventory:manage",
        "orders:fulfill", "orders:read_vendor",
        "payouts:read", "analytics:vendor",
    },
    UserRole.DELIVERY_AGENT: {
        "deliveries:read", "deliveries:update_status", "deliveries:verify_otp",
    },
    UserRole.SUPPORT_AGENT: {
        "users:read", "orders:read_all", "orders:support_action",
        "refunds:initiate", "reviews:moderate",
    },
    UserRole.ANALYST: {
        "analytics:read_all", "reports:generate", "audit_logs:read",
    },
    UserRole.ADMIN: {
        "users:read", "users:manage",
        "vendors:approve", "vendors:manage",
        "catalog:manage", "categories:manage",
        "orders:manage_all", "coupons:manage",
        "zones:manage", "audit_logs:read",
        "analytics:read_all",
    },
    UserRole.SUPER_ADMIN: {
        "*"
    },
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generates a secure bcrypt hash for a password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    role: str = UserRole.CUSTOMER.value,
    expires_delta: Optional[timedelta] = None,
    claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Generates an encoded JWT access token with JTI and expiration."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": subject,
        "role": role,
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    if claims:
        to_encode.update(claims)
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str,
    role: str = UserRole.CUSTOMER.value,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generates an encoded JWT refresh token with rotation JTI."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": subject,
        "role": role,
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT token signature and expiration."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")


def generate_otp(digits: int = 6) -> str:
    """Generates a cryptographically secure numeric OTP."""
    range_start = 10 ** (digits - 1)
    range_end = (10 ** digits) - 1
    return str(secrets.randbelow(range_end - range_start + 1) + range_start)


def has_permission(role: UserRole, required_permission: str) -> bool:
    """Evaluates whether a role possesses a specific permission."""
    perms = ROLE_PERMISSIONS.get(role, set())
    if "*" in perms:
        return True
    return required_permission in perms
