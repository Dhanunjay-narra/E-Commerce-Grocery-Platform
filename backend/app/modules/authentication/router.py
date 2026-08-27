"""Authentication and Session Management API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.authentication.schemas import (
    RegisterRequest,
    LoginRequest,
    OTPRequest,
    OTPVerifyRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
    SessionResponse,
)
from app.modules.authentication.service import AuthService
from app.modules.authentication.permissions import get_current_user, decode_token
from app.modules.users.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Registers a new user account with email/password and returns auth tokens."""
    service = AuthService(db)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    return await service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticates credentials and returns access and refresh tokens."""
    service = AuthService(db)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    return await service.login(payload, ip_address=client_ip, user_agent=user_agent)


@router.post("/otp/request")
async def request_otp(
    payload: OTPRequest,
    db: AsyncSession = Depends(get_db),
):
    """Dispatches a one-time passcode for phone or email verification."""
    service = AuthService(db)
    return await service.request_otp(payload)


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(
    payload: OTPVerifyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Verifies OTP code and authenticates or provisions the user."""
    service = AuthService(db)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    return await service.verify_otp(payload, ip_address=client_ip, user_agent=user_agent)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Rotates an existing refresh token and issues a new access/refresh bundle."""
    service = AuthService(db)
    return await service.refresh_tokens(payload.refresh_token)


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revokes current session."""
    service = AuthService(db)
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    jti = None
    if token:
        try:
            payload = decode_token(token)
            jti = payload.get("jti")
        except Exception:
            pass
    await service.logout(current_user, token_jti=jti)
    return {"success": True, "message": "Successfully logged out."}


@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revokes all active sessions across all devices."""
    service = AuthService(db)
    await service.logout_all(current_user)
    return {"success": True, "message": "All active sessions have been invalidated."}


@router.post("/password/reset-request")
async def password_reset_request(
    payload: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Sends a password reset OTP to the user's verified email."""
    service = AuthService(db)
    return await service.request_otp(OTPRequest(identifier=payload.email, purpose="RESET_PASSWORD"))


@router.post("/password/reset-confirm")
async def password_reset_confirm(
    payload: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """Verifies OTP and resets the account password."""
    service = AuthService(db)
    return await service.confirm_password_reset(payload)


@router.post("/password/change")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Changes the current authenticated user's password."""
    service = AuthService(db)
    return await service.change_password(current_user, payload)


@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists all active device sessions for the authenticated user."""
    service = AuthService(db)
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    jti = None
    if token:
        try:
            payload = decode_token(token)
            jti = payload.get("jti")
        except Exception:
            pass
    return await service.get_user_sessions(current_user, current_jti=jti)
