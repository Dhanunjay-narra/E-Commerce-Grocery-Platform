"""Authentication domain business logic and token management service."""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp,
    UserRole,
)
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    EntityNotFoundError,
    ValidationError,
    PermissionDeniedError,
)
from app.modules.authentication.models import UserSession
from app.modules.authentication.schemas import (
    RegisterRequest,
    LoginRequest,
    OTPRequest,
    OTPVerifyRequest,
    TokenResponse,
    AuthUserResponse,
    SessionResponse,
    PasswordResetConfirm,
    ChangePasswordRequest,
)
from app.modules.authentication.repository import AuthRepository
from app.modules.users.models import User


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AuthRepository(db)

    async def register(self, request: RegisterRequest) -> TokenResponse:
        existing_user = await self.repo.get_user_by_email(request.email)
        if existing_user:
            raise ConflictError("An account with this email address already exists.")

        if request.phone:
            existing_phone = await self.repo.get_user_by_phone(request.phone)
            if existing_phone:
                raise ConflictError("An account with this phone number already exists.")

        role = request.role.upper() if request.role else UserRole.CUSTOMER.value
        if role not in [r.value for r in UserRole]:
            role = UserRole.CUSTOMER.value

        hashed_password = get_password_hash(request.password)
        user = await self.repo.create_user(
            email=request.email,
            hashed_password=hashed_password,
            full_name=request.full_name,
            phone=request.phone,
            role=role,
            is_verified=False,
        )

        return await self._generate_token_bundle(user)

    async def login(self, request: LoginRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> TokenResponse:
        user = await self.repo.get_user_by_identifier(request.email_or_phone)
        if not user:
            await self.repo.record_login_attempt(request.email_or_phone, success=False, ip_address=ip_address, user_agent=user_agent, failure_reason="USER_NOT_FOUND")
            raise AuthenticationError("Invalid email/phone or password.")

        if not user.is_active:
            raise PermissionDeniedError("Your account has been deactivated. Please contact support.")

        if user.lockout_until and user.lockout_until > datetime.now(timezone.utc):
            remaining = int((user.lockout_until - datetime.now(timezone.utc)).total_seconds() / 60)
            raise AuthenticationError(f"Account locked due to multiple failed attempts. Please retry in {max(1, remaining)} minutes.")

        if not user.hashed_password or not verify_password(request.password, user.hashed_password):
            await self.repo.handle_failed_login(user)
            await self.repo.record_login_attempt(request.email_or_phone, success=False, user_id=user.id, ip_address=ip_address, user_agent=user_agent, failure_reason="INVALID_PASSWORD")
            raise AuthenticationError("Invalid email/phone or password.")

        # Reset failed attempts on success
        await self.repo.reset_failed_login(user)
        await self.repo.record_login_attempt(request.email_or_phone, success=True, user_id=user.id, ip_address=ip_address, user_agent=user_agent)

        return await self._generate_token_bundle(user, device_info=request.device_info, ip_address=ip_address, user_agent=user_agent)

    async def request_otp(self, request: OTPRequest) -> dict:
        otp_code = generate_otp(6)
        # Mock mode: Fix OTP to "123456" in dev mode for automated testing/simplicity
        if settings.ENVIRONMENT in ["development", "test"]:
            otp_code = "123456"

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.OTP_EXPIRE_SECONDS)
        await self.repo.create_otp(
            identifier=request.identifier,
            otp_code=otp_code,
            purpose=request.purpose,
            expires_at=expires_at,
        )

        return {
            "success": True,
            "message": f"OTP successfully dispatched to {request.identifier}.",
            "expires_in_seconds": settings.OTP_EXPIRE_SECONDS,
            "mock_otp_for_dev": otp_code if settings.ENVIRONMENT in ["development", "test"] else None,
        }

    async def verify_otp(self, request: OTPVerifyRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> TokenResponse:
        record = await self.repo.get_valid_otp(request.identifier, request.purpose)
        if not record:
            raise ValidationError("Invalid or expired OTP code.")

        if record.otp_code != request.otp_code:
            record.attempts += 1
            if record.attempts >= 5:
                record.is_used = True
            await self.db.flush()
            raise ValidationError("Incorrect OTP code. Please try again.")

        record.is_used = True
        await self.db.flush()

        # Find or create user
        user = await self.repo.get_user_by_identifier(request.identifier)
        if not user:
            # Register on the fly if verified via OTP
            is_email = "@" in request.identifier
            email_val = request.identifier if is_email else f"{request.identifier}@freshcart.local"
            phone_val = None if is_email else request.identifier
            full_name = request.full_name or ("Customer " + request.identifier[-4:] if len(request.identifier) >= 4 else "New Customer")

            user = await self.repo.create_user(
                email=email_val,
                hashed_password=None,
                full_name=full_name,
                phone=phone_val,
                role=UserRole.CUSTOMER.value,
                is_verified=is_email,
                phone_verified=not is_email,
            )
        else:
            if "@" in request.identifier:
                user.is_verified = True
            else:
                user.phone_verified = True
            await self.db.flush()

        return await self._generate_token_bundle(user, ip_address=ip_address, user_agent=user_agent)

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
            jti = payload.get("jti")
            token_type = payload.get("type")
            if not user_id or not jti or token_type != "refresh":
                raise AuthenticationError("Invalid refresh token payload.")
        except Exception:
            raise AuthenticationError("Refresh token is invalid or expired.")

        db_token = await self.repo.get_refresh_token(jti)
        if not db_token or db_token.is_revoked:
            raise AuthenticationError("Refresh token has been revoked or reused.")

        # Rotate refresh token: revoke old one
        await self.repo.revoke_refresh_token(jti)

        user = await self.repo.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User is no longer active.")

        return await self._generate_token_bundle(user)

    async def logout(self, current_user: User, token_jti: Optional[str] = None) -> None:
        if token_jti:
            await self.repo.revoke_session(token_jti)

    async def logout_all(self, current_user: User) -> None:
        await self.repo.revoke_all_user_sessions(current_user.id)

    async def confirm_password_reset(self, request: PasswordResetConfirm) -> dict:
        record = await self.repo.get_valid_otp(request.identifier, "RESET_PASSWORD")
        if not record or record.otp_code != request.otp_code:
            raise ValidationError("Invalid or expired password reset verification code.")

        record.is_used = True
        user = await self.repo.get_user_by_identifier(request.identifier)
        if not user:
            raise EntityNotFoundError("User not found.")

        user.hashed_password = get_password_hash(request.new_password)
        await self.repo.revoke_all_user_sessions(user.id)
        return {"success": True, "message": "Password reset successfully. Please login with your new credentials."}

    async def change_password(self, current_user: User, request: ChangePasswordRequest) -> dict:
        if not current_user.hashed_password or not verify_password(request.old_password, current_user.hashed_password):
            raise ValidationError("Existing password does not match.")

        current_user.hashed_password = get_password_hash(request.new_password)
        await self.repo.revoke_all_user_sessions(current_user.id)
        return {"success": True, "message": "Password updated successfully."}

    async def get_user_sessions(self, current_user: User, current_jti: Optional[str] = None) -> List[SessionResponse]:
        sessions = await self.repo.get_user_sessions(current_user.id)
        return [
            SessionResponse(
                id=s.id,
                device_info=s.device_info,
                ip_address=s.ip_address,
                last_active_at=s.last_active_at,
                is_current=(s.session_token_jti == current_jti),
            )
            for s in sessions
        ]

    async def _generate_token_bundle(
        self,
        user: User,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        import uuid

        access_jti = str(uuid.uuid4())
        access_token = create_access_token(
            subject=user.id,
            role=user.role,
            claims={"jti": access_jti, "email": user.email, "name": user.full_name},
        )

        refresh_jti = str(uuid.uuid4())
        refresh_token = create_refresh_token(subject=user.id, role=user.role)

        session_expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        await self.repo.create_session(
            user_id=user.id,
            session_token_jti=access_jti,
            expires_at=session_expires_at,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        await self.repo.create_refresh_token(
            user_id=user.id,
            token_jti=refresh_jti,
            token_hash=get_password_hash(refresh_token[:30]),
            expires_at=refresh_expires_at,
        )

        user_dto = AuthUserResponse.model_validate(user)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_dto,
        )
